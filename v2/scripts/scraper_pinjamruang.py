import copy
import datetime
import io
import pandas as pd
import urllib.request as ur

from scraper import Scraper


# 2-digit zero-padding.
def zero_pad(num):
    if len(str(num)) == 0:
        return '00'
    elif len(str(num)) == 1:
        return f'0{num}'
    else:
        return str(num)

# The dictionary of commissions in GKI Salatiga.
commission_dict = {
    "Majelis Jemaat": "Majelis Jemaat",
    "KUL": "Komisi Usia Lanjut",
    "KD": "Komisi Dewasa",
    "KP": "Komisi Pemuda",
    "KR": "Komisi Remaja",
    "KA": "Komisi Anak",
    "KPPI": "Komisi Pengajaran dan Pekabaran Injil",
    "KHI": "Komisi Hubungan Internasional",
    "KML": "Komisi Musik dan Liturgi",
    "Komkes": "Komisi Kesejahteraan",
    "KPPK": "Komisi Perkunjungan dan Pelayanan Kematian",
    "Komsarpras dan Mulmed": "Komisi Sarana Prasarana dan Multimedia",
    "KDT": "Komisi Diakonia The Koen Bik",
    "Tim Samaria": "Tim Samaria",
    "Tim Waroeng Tiberias": "Tim Warung Tiberias",
    "Wilayah": "Wilayah",
    "Panitia": "Panitia",
    "TK K 03 Eben Haezer": "TK Kristen 03 Eben Haezer",
    "SD K 03 Eben Haezer": "SD Kristen 03 Eben Haezer",
    "SD K 04 Eben Haezer": "SD Kristen 04 Eben Haezer",
    "SMP K 02 Salatiga": "SMP Kristen 02 Salatiga",
    "Lainnya": "Lainnya",
}

# The mapping of `datetime` module's weekday.
weekday_mapping = {
    0: 'mon',
    1: 'tue',
    2: 'wed',
    3: 'thu',
    4: 'fri',
    5: 'sat',
    6: 'sun',
}


class ScraperPinjamRuang(Scraper):
    
    def __init__(self):
        super().__init__()
        
        # Downloading the online CSV file.
        url = 'https://docs.google.com/spreadsheets/d/1GAvXqBdqp1OGNtLBjZa06jPI7VCaz5JryzZAQCc4Nkk/gviz/tq?tqx=out:csv&gid=265583580'
        fi = ur.urlopen(url)
        csv = fi.read().decode('utf-8')
        
        self.df = pd.read_csv(io.StringIO(csv))

    def run(self):
        super().run()

        # Preamble logging.
        print('Beginning the automation script for updating data: Peminjaman Ruangan')

        # Record all enumerated items.
        enumerated_items = []
        
        for i in range(len(self.df['Timestamp'])):
            name = self.df['Nama Kegiatan / Keperluan'][i]
            
            t = self.df['Waktu Pemakaian Mulai dari'][i].split(':')
            time = zero_pad(t[0]) + ':' + t[1]
            
            t = self.df['Waktu Pemakaian Sampai dengan'][i].split(':')
            time_to = zero_pad(t[0]) + ':' + t[1]
            
            d = self.df['Tanggal Peminjaman'][i].split('/')
            d_y = d[2]
            d_m = zero_pad(d[1])
            d_d = zero_pad(d[0])
            date = d_y + '-' + d_m + '-' + d_d
            
            dt = datetime.date(year=int(d_y), month=int(d_m), day=int(d_d)).weekday()
            weekday = weekday_mapping[ int(dt) ]
            
            place = self.df['Ruangan yang dipakai'][i]
            
            d = self.df['Peminjam'][i]
            representative = commission_dict[d] if d in commission_dict.keys() else d
            
            pic = self.df['Penanggung Jawab'][i]
            
            
            approval = self.df['Persetujuan: [Y] Yes/Disetujui [N] No/Ditolak [W] Wait/Menunggu'][i]
            approval = str(approval).lower().strip()
            if approval not in ['n', 'w', 'y']:
                approval = 'w'  # --- defaults to "waiting for approval".
            
            j = {
                "name": name,
                "time": time,
                "time-to": time_to,
                "timezone": "WIB",
                "date": date,
                "weekday": weekday,
                "type": "proposal",
                "place": place,
                "representative": representative,
                "pic": pic,
                "status": approval,
                "note": ""
            }
            
            enumerated_items.append(j)
        
        self.json_data['data']['agenda-ruangan'] = copy.deepcopy(enumerated_items)
        
        # Write changes.
        super().write(write_msg='agenda-ruangan')

        # Finalizing the script.
        super().finish()


if __name__ == "__main__":
    scraper = ScraperPinjamRuang()
    scraper.run()
