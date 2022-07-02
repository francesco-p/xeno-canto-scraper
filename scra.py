import os
import re
import shutil
import subprocess
from collections import defaultdict
from numpy import int0

import pandas as pd
import requests
from bs4 import BeautifulSoup
from termcolor import cprint
import urllib
import pickle

with open('dic_Common2Class.pkl', 'rb') as f:
    COMMON_2_CLASS = pickle.load(f)

with open('dic_Class2Common.pkl', 'rb') as f:
    CLASS_2_COMMON = pickle.load(f)

COMMON_NAME = { 
    ####### CLASSI NON PREDETTE, MA SBILANCIATE < 30 REC ######
                    # 'akikik': 'Akikiki',
                    # 'bkwpet': 'Black-winged Petrel',
                    # 'coopet': "Cook's Petrel",
                    # 'layalb': 'Laysan Albatross',
                    # 'mauala': 'Maui Alauahio',
                    # 'shtsan': 'Sharp-tailed Sandpiper',
                    # 'bubsan': 'Buff-breasted Sandpiper',
                    # 'akekee': 'Akekee',
                    # 'sopsku1': 'South Polar Skua',
                    # 'bulpet': "Bulwer's Petrel",
                    # 'lessca': 'Lesser Scaup',
                    # 'palila': 'Palila',
                    # 'pomjae': 'Pomarine Jaeger',
                    # 'hudgod': 'Hudsonian Godwit',
                    # 'incter1': 'Inca Tern',
                    # 'akepa1': 'Hawaii Akepa',
                    # 'canvas': 'Canvasback',
                    # 'golphe': 'Golden Pheasant',
                    # 'sooshe': 'Sooty Shearwater',
                    # 'chemun': 'Chestnut Munia',
                    # 'kauama': 'Kauai Amakihi',
                    # 'brnboo': 'Brown Booby',
                    # 'lcspet': "Leach's Storm-Petrel",
                    # 'blknod': 'Black Noddy',
                    # 'oahama': 'Oahu Amakihi',
                    # 'buffle': 'Bufflehead',
                    # 'afrsil1': 'African Silverbill',
                    # 'chbsan': 'Chestnut-bellied Sandgrouse',
                    # 'cintea': 'Cinnamon Teal',
                    # 'gresca': 'Greater Scaup',
                    # 'hawcoo': 'Hawaiian Coot',
                    # 'magpet1': 'Magenta Petrel',
                    # 'grefri': 'Great Frigatebird',
                    # 'kalphe': 'Kalij Pheasant',
                    # 'madpet': "Zino's Petrel",
                    # 'wantat1': 'Wandering Tattler',
                    # 'brnnod': 'Brown Noddy',
                    # 'burpar': 'Burrowing Parakeet',
                    # 'hoomer': 'Hooded Merganser',
                    # 'yebcar': 'Yellow-billed Cardinal',
                    # 'sooter1': 'Sooty Tern',
                    # 'wetshe': 'Wedge-tailed Shearwater',
                    # 'whttro': 'White-tailed Tropicbird',
                    # 'brtcur': 'Bristle-thighed Curlew',
                    # 'masboo': 'Masked Booby',
                    # 'whiter': 'White Tern',
                    # 'glwgul': 'Glaucous-winged Gull',
                    # 'rinduc': 'Ring-necked Duck',
                    # 'norhar2': 'Northern Harrier',
                    # 'fragul': "Franklin's Gull",
                    # 'rettro': 'Red-tailed Tropicbird',
                    # 'ruff': 'Ruff',
                    # 'akiapo':'Akiapolaau',
                    
                    ##### SOLO CLASSI PREDETTE ########
                    'aniani':'Anianiau',
                    'apapan':'Apapane',
                    'barpet':'Band-rumped Storm-Petrel',
                    'crehon':'Akohekohe',
                    'elepai':'Hawaii Elepaio',
                    'ercfra':"Erckel's Francolin",
                    'hawama':'Hawaii Amakihi',
                    'hawcre':'Hawaii Creeper',
                    'hawgoo':'Hawaiian Goose',
                    'hawhaw':'Hawaiian Hawk',
                    'hawpet1':'Hawaiian Petrel',
                    'houfin':'House Finch',
                    'iiwi':'Iiwi',
                    'jabwar':'Javan Bush Warbler',
                    'maupar':'Maui Parrotbill',
                    'omao':'Omao',
                    'puaioh':'Puaiohi',
                    #'skylar':'Eurasian Skylark',
                    'warwhe1':'Warbling White-eye',
                    'yefcan':'Yellow-fronted Canary'
}


def fix_secondary_labels(common_names):
    classes = []
    for common in common_names:
        try:
            c = COMMON_2_CLASS[common]
            classes.append(c)
        except:
            pass
    return classes

def extract_secondary_labels(soup):
    sec_labels_dic = defaultdict(list)
    tooltips = soup.find_all('span', class_='tooltip')
    for tooltip in tooltips:
        elems = [x for x in tooltip.parent.children]
        main_rec_code = elems[-1].get('title').split(':')[0]
        other_spec = elems[-3].attrs['data-qtip-content']
        classes = fix_secondary_labels([x.text for x in BeautifulSoup(other_spec, 'html.parser').find_all('a')])
        sec_labels_dic[main_rec_code] = classes
        
    return sec_labels_dic

def download_and_convert_file(filename, link):
    
    with requests.get(f"https://xeno-canto.org{link}", stream=True) as r:
        print('Download + convert...')
        with open(filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

        # Convert to .ogg and remove .mp3 file
        shell_command = f"ffmpeg -i {filename} -ar 32000 {filename[:-4]}.ogg"
        subprocess.call(shell_command.split())
        
        shell_command = f"rm {filename}"
        subprocess.call(shell_command.split())


def extract_titles_and_links(bird, soup):
    rating_codes = {'A':5, 'B':4, 'C':3, 'D':2, 'E':1 }
    ratings = []
    titles = []
    links = []
    rgx = '<a download=\"(.+) -.* - .*\" href=\"(.+)\">'
    all_a = soup.find_all('a')
    for a in all_a:

        # link and title
        out = re.findall(rgx, str(a))
        if out != []:
            title = out[0][0]
            titles.append(title)
            link = out[0][1]
            links.append(link)

            # Rating
            id_code = link.split('/')[1]
            for li in soup.find_all('li', class_='selected'):
                if li is not None:
                    if li.get('id') is not None:
                        ratings.append(rating_codes[li.text])
                        break

    return titles, links, ratings


def reset_csv():
    header = 'primary_label,secondary_labels,type,latitude,longitude,scientific_name,common_name,author,license,rating,time,url,filename\n'
    with open('metadata.csv', 'w') as f:
        f.write(header)
    print(f'{"CSV RESET":#^80}')
    

def write_row(bird, title, rating, secondary_labels):

    row = f'{bird},"{secondary_labels[title]}",nan,nan,nan,nan,{COMMON_NAME[bird]},nan,nan,{rating},nan,nan,{bird}/{title}.ogg\n'
    with open('metadata.csv', 'a') as f:
        f.write(row)
    return row


###########################################################################################


def main():

    statistics = defaultdict(int)

    if input('Vuoi resettare metadata.csv??? y/n\n') == 'y':
        reset_csv()
        print('CSV resettato')
    else:
        print('CSV non resettato')

    already_downloaded = set(pd.read_csv('train_metadata.csv')['filename'])

    for bird in COMMON_NAME.keys():

        if os.path.isdir(f'./{bird}'):
            print(f"./{bird} Exists")
        else:
            print("Doesn't exists")
            os.mkdir(f'./{bird}')
        
        page = 1
        while True:

            response = requests.get(f"https://xeno-canto.org/explore?query={urllib.parse.quote(COMMON_NAME[bird])}&pg={page}")
            soup = BeautifulSoup(response.content, "html.parser")

            titles, links, ratings = extract_titles_and_links(COMMON_NAME[bird], soup)
            secondary_labels = extract_secondary_labels(soup)
            print(f'Found {len(titles)} records of {bird} at https://xeno-canto.org/explore?query={COMMON_NAME[bird]}&pg={page}')

            # stop downloading if there are no more pages
            # or if we are at the 10 page....enough!
            if titles == [] and links == []:
                break
            if page == 10:
                break

            assert len(titles) == len(links) == len(ratings), f'something wrong {bird} pg: {page}'
            
            for title, link, rating in zip(titles, links, ratings):
                filename = f'./{bird}/{title}.mp3'
                if f"{filename[2:-4]}.ogg" not in already_downloaded:
                    download_and_convert_file(filename, link)
                    row = write_row(bird, title, rating, secondary_labels)
                    cprint(f'{row}', 'cyan')
                    cprint(f'[DOWNLOAD]   {filename} rating {rating}', 'green')
                    statistics[bird] = statistics[bird]+1
                else:
                    print(f'[PRESENT]   {filename} rating {rating}')
                
            page += 1

    print(f'Class and number of recordings found:')
    print(statistics)

if __name__ == "__main__":
    main()
    