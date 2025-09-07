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

# The day keys.
day_keys_dict = {
    "Minggu": "sun",
    "Senin": "mon",
    "Selasa": "tue",
    "Rabu": "wed",
    "Kamis": "thu",
    "Jumat": "fri",
    "Sabtu": "sat",
}

# The dictionary of commissions in GKI Salatiga.
commission_dict = {
    "Kantor": "Kantor Tata Usaha GKI Salatiga",
    "MJ": "Majelis Jemaat",
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
    "TIM WARTIB": "Tim Warung Tiberias",
    "Tim Waroeng Tiberias": "Tim Warung Tiberias",
    "Wilayah": "Wilayah",
    "WILAYAH": "Wilayah",
    "Panitia": "Panitia",
    "TK K 3": "TK Kristen 03 Eben Haezer",
    "TK K 03 Eben Haezer": "TK Kristen 03 Eben Haezer",
    "SD K 3": "SD Kristen 03 Eben Haezer",
    "SD K 03 Eben Haezer": "SD Kristen 03 Eben Haezer",
    "SD K 4": "SD Kristen 04 Eben Haezer",
    "SD K 04 Eben Haezer": "SD Kristen 04 Eben Haezer",
    "SMP K 2": "SMP Kristen 02 Salatiga",
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


class ScraperAgenda(Scraper):
    
    def __init__(self):
        super().__init__()
        
        # Downloading the online CSV files.
        # ---
        # "PR" stands for "Pinjam Ruang".
        url = 'https://docs.google.com/spreadsheets/d/1GAvXqBdqp1OGNtLBjZa06jPI7VCaz5JryzZAQCc4Nkk/gviz/tq?tqx=out:csv&gid=265583580'
        fi = ur.urlopen(url)
        csv = fi.read().decode('utf-8')
        self.df_pr = pd.read_csv(io.StringIO(csv))
        del url, fi, csv
        # ---
        # "AR" stands for "Agenda Rutin".
        url = 'https://docs.google.com/spreadsheets/d/1GAvXqBdqp1OGNtLBjZa06jPI7VCaz5JryzZAQCc4Nkk/gviz/tq?tqx=out:csv&gid=1336399950'
        fi = ur.urlopen(url)
        csv = fi.read().decode('utf-8')
        self.df_ar = pd.read_csv(io.StringIO(csv))
        del url, fi, csv
    
    def scrape_pinjamruang_v2(self):
        
        # Preamble logging.
        print('Beginning the automation script for updating data: Peminjaman Ruangan')

        # Record all enumerated items.
        enumerated_items = []
        
        for i in range(len(self.df_pr['Timestamp'])):
            name = self.df_pr['Nama Kegiatan / Keperluan'][i]
            
            t = self.df_pr['Waktu Pemakaian Mulai dari'][i].split(':')
            time = zero_pad(t[0]) + ':' + t[1]
            
            t = self.df_pr['Waktu Pemakaian Sampai dengan'][i].split(':')
            time_to = zero_pad(t[0]) + ':' + t[1]
            
            d = self.df_pr['Tanggal Peminjaman'][i].split('/')
            d_y = d[2]
            d_m = zero_pad(d[1])
            d_d = zero_pad(d[0])
            date = d_y + '-' + d_m + '-' + d_d
            
            dt = datetime.date(year=int(d_y), month=int(d_m), day=int(d_d)).weekday()
            weekday = weekday_mapping[ int(dt) ]
            
            place = self.df_pr['Ruangan yang dipakai'][i]
            
            d = self.df_pr['Peminjam'][i]
            representative = commission_dict[d] if d in commission_dict.keys() else d
            
            pic = self.df_pr['Penanggung Jawab'][i]
            
            notes = self.df_pr['Keterangan Tambahan'][i]
            if str(notes).lower() == 'nan':
                notes = ''
            
            approval = self.df_pr['Persetujuan'][i]
            approval = str(approval).strip()
            
            # Translate human-readable to machine-readable.
            approval = approval.replace('Dibatalkan Pemohon', 'c')
            approval = approval.replace('Ditolak', 'n')
            approval = approval.replace('Menunggu Persetujuan', 'w')
            approval = approval.replace('Disetujui', 'y')
            
            if approval not in ['c', 'n', 'w', 'y']:
                approval = 'w'  # --- defaults to "waiting for approval".
            
            j = {
                "name": str(name),
                "time": str(time),
                "time-to": str(time_to),
                "timezone": "WIB",
                "date": str(date),
                "weekday": str(weekday),
                "type": "proposal",
                "place": str(place),
                "representative": str(representative),
                "pic": str(pic),
                "status": str(approval),
                "note": str(notes)
            }
            
            enumerated_items.append(j)
        
        self.json_data['data']['agenda-ruangan'] = copy.deepcopy(enumerated_items)
    
    def scrape_rutin_v2(self):
        
        # Preamble logging.
        print('Beginning the automation script for updating data: Agenda Rutin')
        
        # Temporary dict.
        temp_dict = {}
        for l in list(day_keys_dict.values()):
            temp_dict[l] = list()
        
        for i in range(len(self.df_ar['Hari'])):
            name = self.df_ar['Nama Kegiatan'][i]
            
            t = self.df_ar['Waktu Dari'][i].split(':')
            time = zero_pad(t[0]) + ':' + t[1]
            
            t = self.df_ar['Waktu Ke'][i].split(':')
            time_to = zero_pad(t[0]) + ':' + t[1]
            
            d = self.df_ar['Hari'][i]
            weekday = day_keys_dict[d]
            
            place = self.df_ar['Tempat'][i]
            
            d = self.df_ar['PIC'][i]
            representative = commission_dict[d] if d in commission_dict.keys() else d
            if str(representative).lower() == 'nan':
                representative = ''
            
            notes = self.df_ar['Catatan Tambahan'][i]
            if str(notes).lower() == 'nan':
                notes = ''
            
            j = {
                "name": str(name),
                "time": str(time),
                "time-to": str(time_to),
                "timezone": "WIB",
                "type": "rutin",
                "place": str(place),
                "representative": str(representative),
                "note": str(notes)
            }
            
            # Appending the data.
            temp_dict[weekday].append(copy.deepcopy(j))
            del j
        
        # Sorting by ascending "time" order.
        for l in list(day_keys_dict.values()):
            temp_dict[l] = sorted(temp_dict[l], key=lambda m: m['time'])
        
        # Reseting the current agenda items.
        self.json_data['data']['agenda'] = copy.deepcopy(temp_dict)

    def run(self):
        super().run()
        
        # Run the scrapers.
        self.scrape_pinjamruang_v2()
        self.scrape_rutin_v2()
        
        # Write changes.
        super().write(write_msg='agenda')

        # Finalizing the script.
        super().finish()


if __name__ == "__main__":
    scraper = ScraperAgenda()
    scraper.run()
