import pandas as pd

inmates_df = pd.read_csv('bill.csv')
month = 'JAN'
year = 2025


for index, inmate in inmates_df.iterrows():
    name: str = inmate['name'].upper()
    inmate_id = inmate['inmate_id']
    reference: str = f'{inmate_id}{month}{year}'
    note = f'{inmate_id} {name} {inmate['department']} MESS BILL {month} {year}'

    if len(note) > 49:
        name = name.split(' ')[0]
        note = f'{inmate['inmate_id']} {name} {inmate['department']} MESS BILL {month} {year}'

        if len(note) > 49:
            note = f'{inmate['inmate_id']} {name} {inmate['department']} M BILL {month} {year}'

            if len(note) > 49:
                note = ''

    note = note.replace(' ', '%20')
    upi_url = f'upi://pay?pa=gc2003unni@okhdfcbank&pn=Gokul%20c&am={inmate['amount']}&tn={note}&tr={reference}&aid=uGICAgMCAgdjGGw'

    print(f'{name}: {upi_url}')