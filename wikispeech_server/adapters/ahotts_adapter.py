import os, re, sys, hashlib, struct, socket, requests

if __name__ == "__main__":
    sys.path.append(".")

import wikispeech_server.log as log
import wikispeech_server.config as config

cwdir = os.getcwd()
tmpdir = config.config.get("Audio settings","audio_tmpdir")
ahotts_server_ip = config.config.get("Services", "ahotts_server_ip")
ahotts_server_port = config.config.get("Services", "ahotts_server_port")
ahotts_speed = config.config.get("Services", "ahotts_speed")

units_eu=[
'Kg',
'Km',
'cl',
'cm',
'dm',
'g',
'l',
'm',
'm2',
'ml',
'mm',
]

abbreviations_eu=[
'I.',
'II.',
'III.',
'IV.',
'V.',
'VI.',
'VII.',
'VIII.',
'IX.',
'X.',
'XI.',
'XII.',
'XIII.',
'XIV.',
'XV.',
'XVI.',
'XVII.',
'XVIII.',
'XIX.',
'XX.',
'XXI.',
'XXII.',
'XXIII.',
'XXIV.',
'XXV.',
'A.',
'abelazk.',
'admin.',
'admin.zuz.',
'aeron.',
'Af.',
'aizk.',
'albait.',
'alj.',
'alk.',
'alp.',
'Am.',
'anat.',
'anestesiol.',
'animis.',
'antr.',
'antz.',
'argazk.',
'arit.',
'arkit.',
'arm.',
'arraunk.',
'art.ed.',
'art.graf.',
'astrol.',
'astron.',
'astronaut.',
'autom.',
'B.',
'bnaf.',
'bakter.',
'barzz.',
'basog.',
'beirag.',
'ber.',
'biof.',
'biogeog.',
'biokim.',
'biol.',
'bizk.',
'bolb.',
'bot.',
'box.',
'C.',
'D.',
'dek.',
'dem.',
'dermat.',
'didak.',
'diet.',
'diplom.',
'E.',
'EAm.',
'edafol.',
'ehiz.',
'ehung.',
'ekol.',
'ekon.',
'elek.',
'elektroak.',
'elektrobiol.',
'elektrol.',
'elektrom.',
'elektron.',
'elektrorradiol.',
'elektrost.',
'elektrotek.',
'enbriol.',
'endokr.',
'enol.',
'entom.',
'epistem.',
'eraik.',
'erl.',
'erloj.',
'erlzz.',
'erradiol.',
'erradiot.',
'erret.',
'errg.',
'erronk.',
'esgr.',
'eskol.',
'eskub.',
'eskular.',
'est.',
'estat.',
'estil.',
'estrat.',
'etik.',
'etim.',
'etnogr.',
'etnol.',
'etol.',
'Eur.',
'eusk.zuz.',
'F.',
'f.zuz.',
'farmakol.',
'fenol.',
'fenomenol.',
'fil.',
'filat.',
'filol.',
'fin.zuz.',
'finantz.',
'fis.',
'fis.atom.',
'fis.nukl.',
'fisiol.',
'fisiopat.',
'fitogeog.',
'fitol.',
'fitopatol.',
'fitosoz.',
'fonet.',
'fonol.',
'fut.',
'G.',
'G.E.T.',
'g.b.',
'garag.',
'geneal.',
'genet.',
'geobot.',
'geod.',
'geofis.',
'geogn.',
'geogr.',
'geol.',
'geom.',
'geomorfol.',
'gimn.',
'ginek.',
'gip.',
'glaziol.',
'gliziol.',
'glotod.',
'gozog.',
'gram.',
'HAm.',
'halt.',
'har.-jas.',
'harg.',
'heg.',
'hegt.hazk.',
'hegtzz.',
'helmint.',
'hematol.',
'her.kir.',
'herald.',
'herm.',
'hezk.',
'hidraul.',
'hidrodin.',
'hidrogr.',
'hidrol.',
'hidrost.',
'hidrot.',
'hig.',
'higrom.',
'hirgz.',
'hist.',
'histaur.',
'histol.',
'hizkl.',
'hock.',
'homeop.',
'IAm.',
'igelts.',
'iger.',
'ikon.',
'iktiol.',
'ikus.',
'inform.',
'ingen.',
'ipar.',
'irr.',
'irrtek.',
'itsas.',
'itsas.zi.',
'J.',
'jak.',
'jantzig.',
'jd.',
'jok.',
'jost.',
'jurispr.',
'k.a.',
'K.a.',
'k. a.',
'K. a.',
'k.o.',
'K.o.',
'k. o.',
'K. o.',
'kardiol.',
'kartogr.',
'kartzinol.',
'kazet.',
'kb.',
'kim.',
'kirg.',
'kirol.',
'klimat.',
'kont.',
'koop.elk.',
'koop.s.',
'koreogr.',
'kosm.',
'kosmetol.',
'kriminol.',
'kriptogr.',
'kristalogr.',
'L.',
'l.g.',
'lan.zuz.',
'lap.',
'larrug.',
'ling.',
'liter.',
'litogr.',
'log.',
'logist.',
'lorezz.',
'M.',
'mahastzz.',
'malakol.',
'mam.',
'mat.',
'mb.',
'meatz.',
'med.',
'mek.',
'merkat.',
'merkat.zuz.',
'metaf.',
'metal.',
'metalogr.',
'meteorol.',
'metod.',
'metr.',
'metrol.',
'mikol.',
'mikrob.',
'mikroek.',
'mikrogr.',
'mil.',
'miner.',
'mit.',
'mor.',
'morfol.',
'mus.',
'N.',
'nab.',
'naf.',
'nart.zuz.',
'naut.',
'nekaz.',
'neur.',
'neurofis.',
'neurol.',
'numism.',
'O.',
'obst.',
'odont.',
'oftalmol.',
'oihanlz.',
'oinet.',
'opt.',
'ornitol.',
'ortogr.',
'otarg.',
'oz.',
'ozeanogr.',
'P.',
'p.b.',
'p.d.',
'p.k.',
'p.ku.',
'p.s.',
'paleobot.',
'paleogr.',
'paleont.',
'paleoz.',
'paperg.',
'parapsikol.',
'patol.',
'pedag.',
'pediatr.',
'petrogr.',
'petrokim.',
'pil.',
'pint.',
'pirotek.',
'pneumol.',
'poet.',
'pol.',
'pros.',
'psikiatr.',
'psikol.',
'Q.',
'R.',
'S.',
'saskib.',
'saskig.',
'sem.',
'semiol.',
'semiot.',
'serol.',
'sideromet.',
'sint.',
'soziol.',
'St.',
'sukald.',
'T.',
'taurom.',
'tb.',
'teknol.',
'telegr.',
'telekom.',
'teol.',
'terap.',
'teratol.',
'term.',
'termodin.',
'termom.',
'topog.',
'topon.',
'toxik.',
'trig.',
'txirrind.',
'U.',
'u.e.',
'urol.',
'urreg.',
'W.',
'Y.',
'Z.',
'zar.',
'zeram.',
'zerg.zuz.',
'zeta-hazk.',
'zez.',
'ziber.',
'zientz.',
'zig.zuz.',
'zin.',
'zineg.',
'zirk.',
'zirkl.',
'zit.',
'zool.',
'zootek.',
'zub.',
'zuhaizl.',
'zurg.',
'zuz.err.',
'zuz.hist.',
'zuz.kan.',
'zuz.orok.',
'zuz.pol.',
'zuz.proz.',
'zuz.zib.',
'a.-k.',
'a.m.',
'abe.',
'abl.',
'abs.',
'abstr.',
'abu.',
'ad.',
'ad.-konpl.',
'adb.',
'adib.',
'adj.',
'adl.',
'adlag.',
'ag.',
'aip.',
'akt.',
'akus.',
'al.',
'ald.',
'aldib.',
'alt.',
'and.',
'andño.',
'anfib.',
'anim.',
'anton.',
'api.',
'aptu.',
'arakn.',
'arg.',
'argit.',
'ark.',
'arr.',
'arrunk.',
'art.',
'artrop.',
'arzki.',
'as.',
'auton.',
'auton.-erk.',
'auz.',
'az.',
'aza.',
'azal.',
'azk.',
'año.',
'banatz.',
'bas.',
'batx.',
'batz.',
'bazk.',
'bibl.',
'bibliog.',
'bid.',
'bizt.',
'bol.',
'brakiop.',
'briof.',
'brioz.',
'btz.',
'btz.arr.',
'btz.orok.',
'btzkde.',
'bul.',
'dat.',
'dekl.',
'dest.',
'det.',
'dial.',
'diam.',
'dib.',
'dptu.',
'dtu.',
'e.a.',
'e.b.',
'ebol.',
'ed.',
'eg.',
'egiazt.',
'eka.',
'ekinod.',
'elektromag.',
'elk.',
'emak.',
'enp.',
'enpr.',
'ent.',
'er.',
'erak.',
'eransk.',
'erat.',
'erg.',
'erk.',
'erref.',
'esk.',
'eskl.',
'eskra.',
'esp.',
'esr.zah.',
'etab.',
'etc.',
'etorb.',
'eusk.',
'ezk.',
'fam.',
'fanerog.',
'fem.',
'fra.',
'g.g.b.',
'gaitz.',
'gald.',
'gastrop.',
'gen.',
'ger.',
'giz.',
'guzt.',
'h.',
'h.-adl.',
'hausn.',
'hegt.',
'hizk.',
'hizt.',
'ibde.',
'ibid.',
'id.',
'ig.',
'ik.',
'ilustr.',
'inf.',
'infrakl.',
'ins.',
'instr.',
'int.',
'interj.',
'ints.',
'ira.',
'irag.',
'iz.',
'iz.-konpl.',
'iz.arr.',
'iz.pr.',
'izenb.',
'izlag.',
'izond.',
'izord.',
'izpta.',
'jn.',
'jn./and.',
'jr.',
'junt.',
'jur.',
'k.',
'kap.',
'kl.',
'koadr.',
'konts.',
'koop.',
'kop.',
'krust.',
'ktu.kte.',
'l.-gen.',
'lab.',
'lehend.',
'lib.',
'lok.',
'lr.',
'luz.',
'luzp.',
'm.-adl.',
'mai.',
'maiusk.',
'mar.',
'mask.',
'max.',
'mend.',
'min.',
'minusk.',
'mot.',
'mug.',
'mug.pl.',
'mug.sg.',
'mugg.',
'mugtz.',
'multz.',
'nag.',
'narr.',
'neol.',
'nom.',
'obj.',
'og.',
'oh.',
'onomat.',
'or.',
'ord.',
'ornd.',
'orng.',
'orok.',
'orr.',
'ots.',
'p.m.',
'p.p.m.',
'part.',
'partik.',
'partiz.',
'pas.',
'pei.',
'perp.',
'perts.',
'pl.',
'postpos.',
'pred.',
'pres.',
'prim.',
'prob.',
'pta.',
'pzta.',
'seg.',
'sin.',
'sing.',
'sist.',
'sol.',
'soz.',
'sp.',
'spp.',
'ssp.',
'stua.',
'subdib.',
'subfam.',
'subfil.',
'subg.',
'subj.',
'subkl.',
'subord.',
'subsp.',
'subst.',
'superfam.',
'superkl.',
'superord.',
'tel.',
'tetrap.',
'tf.',
'unib.',
'unit.',
'urr.',
'urt.',
'uzt.',
'var.',
'vid.',
'z.g.',
'zbko.',
'zefalop.',
'zenb.',
'zet.',
'zk.',
'ztua.',
'zum.',
'zuz.',
'Ñ.',
]
foreign_eu=[
'Attacks',
'Aamann',
'Abbey',
'Abdurrahman',
'Abernathy',
'Abruzzo',
'Acehn',
'Affret',
'Aguilar',
'Aguirre',
'AhoTTS',
'Aitzpea',
'Ajaccio',
'Albright',
'Aleksandr',
'Almería',
'Alshton',
'Amann',
'Angel',
'Ángel',
'Angela',
'Ángela',
'Aregahegn',
'Arguedas',
'Armagh',
'Armagnac',
'armagnac',
'Armspach',
'Armstrong',
'Athletic',
'Athletik',
'Avignon',
'avilar',
'Biaggi',
'Brooks',
'Bruijn',
'Babcock',
'Backstedt',
'Badmarsh',
'Barnstormer',
'Bayrouth',
'Bayonne',
'Beckstein',
'Behnud',
'Bergkamp',
'Bergman',
'Bernd',
'Bigelow',
'Bilborock',
'Bjork',
'Bjorklund',
'Black',
'Blijlevens',
'Boardman',
'Borgnine',
'Bosnia-Herzegovina',
'Brahms',
'Brazzaville',
'Bretchen',
'bridge',
'Bridgetown',
'bridgetowndar',
'British',
'Brondby',
'Brothers',
'Bruckner',
'Brundtland',
'Bucks',
'Bugs',
'Bullock',
'Burgner',
'Bush',
'Buzmann',
'by-pass',
'by',
'bypass',
'byte',
'Bychkov',
'cowboy',
'Camps',
'cappuccino',
'Carrickfergus',
'Catalunya',
'catch',
'catcher',
'Cathy',
'Celtics',
'Cerdanya',
'Chahartugchi',
'Chann',
'chauvinismo',
'chauvinista',
'Chouck',
'Chris',
'Christelle',
'Christian',
'Christina',
'Christine',
'Christopher',
'churrigueresko',
'churriguerismo',
'Clercq',
'Cockbain',
'Cognac',
'cognac',
'Colutchio',
'copyright',
'cromagnon',
'Cronenberg',
'Crooks',
'Cruyff',
'curaçao',
'Donaghmore',
'Dvorak',
'Dahlan',
'Darritchon',
'Darwish',
'darwinismo',
'darwinista',
'Davids',
'Death',
'Debby',
'Decoexsa',
'dekanewton',
'Dejoehnetteren',
'Dempsey',
'Deschamps',
'deuce',
'Diack',
'Dick',
'Dimitrij',
'disc-jockey',
'Djalminha',
'Djamolidin',
'Djolonga',
'Djukanovic',
'Donaldson',
'Dormund',
'Dortmund',
'Dortmunt',
'Downing',
'Dredsner',
'Dresdner',
'Elizabeth',
'Eduards',
'Eideann',
'Eskandinavia',
'eskandinaviar',
'Euskonews',
'Falls',
'Fatih',
'Feinn',
'Fericgla',
'Flecktones',
'Flintoff',
'Flynn',
'Franck',
'Fredsgaard',
'Freetown',
'freetowndar',
'Fribourg',
'Fuenl',
'Furundzija',
'Gwiazdowski',
'Garvaghy',
'Gayssot',
'Geoffrey',
'Georgetown',
'georgetowndar',
'Giggs',
'Gillick',
'Glenn',
'Gnasher',
'Greenpeace',
'Guggenheim',
'Guinness',
'Hackman',
'Hagans',
'Haggis',
'Hallmark',
'Hannover',
'Hans',
'Hawaii',
'heavy',
'Henning',
'Herzegovina',
'herzegovinar',
'Herzl',
'Hibbert',
'hippy',
'hockey',
'Hoffman',
'Hooks',
'Hruska',
'Humboldt',
'husky',
'Jaksche',
'jaffna',
'Janck',
'Jann',
'Jarmusch',
'Jastrjembskik',
'Javier',
'Jazzle',
'Joerg',
'Johann',
'Johnny',
'Jupp',
'Kahn',
'Kallsberg',
'Kathy',
'kb',
'Keith',
'Kellman',
'Kenya',
'kenyar',
'Kevin',
'Kfor',
'Khokhlov',
'Kidd',
'kilobyte',
'King',
'Kingsnakes',
'Kingstown',
'kingstowndar',
'Kiratdzé',
'kirsch',
'kitsch',
'Kitzsteinhorn',
'knock-out',
'Kuhbauer',
'Kurth',
'Livingston',
'Lahtinen',
'Landcent',
'Languedoc',
'lasagna',
'Leonhardt',
'Liechtenstein',
'Lilongwe',
'lilongwetar',
'Lindsay',
'Liq',
'Lovaina',
'Mendelssohn',
'Mahler',
'Malvin',
'malvinar',
'Mann',
'Mapfre',
'Marcelina',
'Marcelino',
'Marshall',
'Martens',
'Martti',
'Mavericks',
'mb',
'McCain',
'McCarty',
'McCaskill',
'McDermott',
'McGrady',
'McKenzie',
'McKeown',
'McKiernan',
'McLaren',
'McLaughlin',
'McLeod',
'McManaman',
'Merckx',
'Miguel',
'Mills',
'Milosz',
'Minerva',
'Minh',
'Monlong',
'Mons',
'Monterrey',
'Montferrand',
'Montgomery',
'Mpenza',
'Murphy',
'Museeuw',
'music-hall',
'Mª',
'NDour',
'Night',
'navajo',
'Networks',
'New',
'Newton',
'Newtondar',
'Nick',
'Nietzsche',
'Northampton',
'Northern',
'nylon',
'oktiabrskaia',
'Overmars',
'Pack',
'Padrnos',
'Pavlowitch',
'Peck',
'Phoblacht',
'pidgin',
'Qatar',
'Ralph',
'Reberb',
'Records',
'reggae',
'Reggie',
'Regginan',
'Reynolds',
'Ribbeck',
'Rights',
'rock-and-roll',
'Roth',
'Rotislavs',
'Rusedski',
'Rush',
'Sarajevo',
'Steels',
'Supersonics',
'sarajevoar',
'Scala',
'Scarlatti',
'Scatoline',
'Schade',
'Schaeubleren',
'Schaueble',
'Schmeichel',
'Schmiden',
'Schmidt',
'Schnabelek',
'Schneider',
'Scholl',
'Schommer',
'Schroeder',
'Schumacher',
'Science',
'Scola',
'Scordatura',
'Scottish',
'Scudamore',
'seguidilla',
'Severina',
'Severino',
'Shirreff',
'Simpson',
'Siverttson',
'Skleranikova',
'Smetanine',
'smog',
'Soderberg',
'Southworth',
'Space',
'Speight',
'Spencer',
'Spiegel',
'Spike',
'Split',
'Spokaite',
'Sponeck',
'Sports',
'Springfield',
'Srebenica',
'Sri',
'Stade',
'Stam',
'Stankovic',
'Stanley',
'Stansted',
'Staporn',
'Stars',
'Steve',
'Stewart',
'Sting',
'Stormes',
'Storojev',
'Stradivarius',
'Strand',
'Strauss',
'Straw',
'Streisand',
'Sven',
'Svorada',
'swahili',
'Swansea',
'Swazilandia',
'swazilandiar',
'Teaching',
'TermBret',
'Thompson',
'Thornton',
'Todd',
'Townsend',
'Trzeciak',
'Tsvangirai',
'Tudjman',
'Txukhrai',
'Ullrich',
'Undertakers',
'Utah',
'Vaduz',
'Valentin',
'Valentín',
'Valentina',
'Vaughters',
'Verbrugghe',
'Vergnani',
'Virgilio',
'Virginia',
'Voskamp',
'Vucitrn',
'Wesemann',
'wahhabismo',
'Walsh',
'Washington',
'Watch',
'Webben',
'Wellington',
'Wells',
'Wilkingsburg',
'Wiltberger',
'Winnick',
'Wojciech',
'Wolfensohn',
'Woods',
'Wyoming',
'Xevardnadze',
'Xfera',
'Zajick',
'Zberg',
'Ahmed',
'andamp',
'Anne',
'attrezzo',
'Back',
'boomerang',
'Casals',
'Clippers',
'Days',
'Deutsch',
'Djindic',
'Djindjic',
'Djokar',
'Domecq',
'Dominique',
'Emgann',
'Fischler',
'Flack',
'Flash',
'Fnac',
'Frankfurt',
'Fuhrer',
'Girls',
'Girondins',
'grizzly',
'Hemingway',
'High',
'hobby',
'Irish',
'Jack',
'Jackson',
'jacuzzi',
'Jazz',
'jazz-band',
'jazzaldi',
'jazzlari',
'Jeff',
'Joglars',
'John',
'Johnson',
'Joseph',
'karting',
'Knorr',
'Knörr',
'Kohl',
'light',
'Lincoln',
'Macclean',
'Massachussetts',
'merengue',
'mezzoforte',
'mezzopiano',
'mezzosoprano',
'Molotoff',
'Molotov',
'muezzin',
'Nasdaq',
'off',
'paparazzi',
'Patrick',
'Pays',
'pedrazzin',
'Peggy',
'Perpinya',
'Perpinyà',
'Petersburg',
'Petersburgo',
'Phreaker',
'pizza',
'pizzeria',
'pizzicato',
'puzzle',
'Racing',
'ragazza',
'Rattle',
'razzia',
'Richardson',
'Rolls',
'Rudolph',
'Scot',
'Scott',
'Seattle',
'shock',
'Sinn',
'skinhead',
'Sky',
'Slobodan',
'Smith',
'software',
'speed',
'Spice',
'sport',
'Sporting',
'Sprilur',
'squash',
'Stalin',
'Stampa',
'stand',
'Stanford',
'Star',
'State',
'status',
'Stefano',
'Stephane',
'Stephen',
'stock',
'stop',
'Stormont',
'Street',
'Sweet',
'techno',
'Thatcher',
'thriller',
'trekking',
'Txernobyl',
'Volkswagen',
'Watchmen',
]

initials_eu=[
'A3',
'AB',
'ABB',
'ABK',
'ABS',
'ACB',
'ACT',
'ADN',
'AE',
'AEB',
'AEK',
'AFM',
'AHN',
'AHT',
'ARN',
'BBB',
'BBC',
'BBK',
'BBVA',
'BEZ',
'BNG',
'BPG',
'BPN',
'BP',
'BSCH',
'C+',
'CANAL+',
'CCOO',
'CDCA',
'CDC',
'CDN',
'CD-ROM',
'CDU',
'CEST',
'CET',
'CFDT',
'CGPJ',
'CGT',
'CNN',
'CNT',
'CO2',
'CPT',
'CRS',
'CTP',
'DBH',
'DBHO',
'DIPC',
'DJ',
'DNA',
'DNI',
'DV',
'DVD',
'EA',
'EAE',
'EAJ',
'EB',
'EB-IU',
'EBB',
'EBZ',
'EE',
'EEBB',
'EEE',
'EGA',
'EGM',
'EH',
'EHAA',
'EHBO',
'EHE',
'EHGAM',
'EHKME',
'EHNE',
'EHSF',
'EHU',
'EHU-UPV',
'EI',
'EIE',
'EITB',
'EJ',
'EKB',
'ELB',
'ESK',
'ET',
'ETB',
'ETE',
'EUSTAT',
'EZLN',
'FFAA',
'FLNC',
'FMI',
'FMLN',
'FPOE',
'FTP',
'FV',
'GBB',
'GGKE',
'GIB',
'GKE',
'GPS',
'HABE',
'HAEE',
'HB',
'HDZ',
'HIES',
'HPIN',
'HPS',
'HSLS',
'I+G',
'I+G+B',
'IAT',
'IBB',
'IFK',
'IK',
'IRALE',
'IRC',
'KEM',
'KLN',
'KPI',
'KPN',
'La2',
'LANE',
'LGS',
'LH',
'LK',
'LPEE',
'LPEZ',
'LSD',
'LVF',
'MDC',
'NA',
'NAN',
'NATO',
'NBA',
'NBE',
'NDF',
'NK',
'NOB',
'NPG',
'NPN',
'NUIZ',
'NUP',
'OEVP',
'OHE',
'OHL',
'OHO',
'OLT',
'OME',
'PFEZ',
'PGA',
'PNV',
'PP',
'PSE',
'PSE-EE',
'PSN',
'PSOE',
'PTP',
'PYME',
'RNA',
'ROM',
'RPR',
'RTVE',
'SA',
'SESB',
'SGAE',
'SK',
'SM',
'SMS',
'SNP',
'T5',
'TAO',
'TB',
'Tele5',
'TVE',
'TV',
'UBG',
'UBI',
'UCD',
'UCPMB',
'UEU',
'UFF',
'UGT',
'UNED',
'UNESCO',
'UNICEF',
'UPN',
'UPV',
'UPV-EHU',
'URL',
'USB',
'UZEI',
'WMO',
'WWF',
'ZIU',
]

specials_eu=units_eu+initials_eu+abbreviations_eu+foreign_eu
specials_eu.sort()

def socket_write_filelength_file(tts_socket,filename):
    file_length=os.stat(filename).st_size
    length_struct=struct.Struct('11s')
    length_struct_packed=length_struct.pack(str(file_length).encode('utf-8'))
    totalsent=0
    while totalsent<len(length_struct_packed):
        sent=tts_socket.send(length_struct_packed[totalsent:])
        if sent==0:
            raise RuntimeError("socket connection broken")
        totalsent=totalsent+sent
    inputfile=open(filename,"rb")
    left=inputfile.read(1024)
    while (left):
        sent=tts_socket.send(left)
        if sent==0:
            raise RuntimeError("socket connection broken")
        left=inputfile.read(1024)
    inputfile.close()

def socket_read_filelength_file(tts_socket):
    chunks=[]
    bytes_recd=0
    while bytes_recd<11:
        chunk=tts_socket.recv(11-bytes_recd)
        if chunk==b'':
            raise RuntimeError("socket connection broken")
        chunks.append(chunk)
        bytes_recd=bytes_recd+len(chunk)
    length_struct_packed=b''.join(chunks)
    length_struct=struct.Struct('11s')
    file_length=length_struct.unpack(length_struct_packed)[0]
    file_length=file_length[:file_length.find(b'\x00')]
    file_length=int(file_length)
    chunks=[]
    bytes_recd=0
    while bytes_recd<file_length:
        chunk=tts_socket.recv(min(file_length-bytes_recd,2048))
        if chunk==b'':
            raise RuntimeError("socket connection broken")
        chunks.append(chunk)
        bytes_recd=bytes_recd+len(chunk)
    return b''.join(chunks)


def synthesise(lang, voice, utterance, presynth=False, hostname=None):
    log.info("Utterance: %s" % utterance)
    input = utterance['original_text']
    log.info("Text: %s" % input)
    words = get_orth(utterance)
    log.info("Words: %s" % words)

    hashstring=input+'&Lang='+lang+'&Voice='+voice['name']
    
    try:
        hash_object=hashlib.md5(hashstring.encode('latin-1'))
    except:
        try:
            hash_object=hashlib.md5(hashstring.encode('utf-8'))
        except:
            hash_object=hashlib.md5(hashstring.encode())
    hashnumber=hash_object.hexdigest()

    """ Call to tts_client, only works if ahotts is installed in same server as wikispeech_mockup. Better to make socket calls over the network.
    inputfile=open("%s/bin/tts_%s.txt" % (ahotts_dir, hashnumber),"wb")
    inputfile.write(input.encode('latin-1')+'\n'.encode('latin-1'))
    inputfile.close()
    ahotts_command = "cd %s/bin ; ./tts_client -SetDur=y -Speed=%s -IP=%s -Port=%s -InputFile=tts_%s.txt -OutputFile=tts_%s.wav -WordFile=tts_%s.wrd -PhoFile=tts_%s.pho ; mv tts_%s.wav %s/%s/tts_%s.wav ; rm tts_%s.txt" % (ahotts_dir, ahotts_speed, ahotts_server_ip, ahotts_server_port, hashnumber, hashnumber, hashnumber, hashnumber, hashnumber, cwdir, tmpdir, hashnumber, hashnumber)
    log.info("Ahotts command: %s" % ahotts_command)
    os.system(ahotts_command)
    audio_url = "%s%s/%s" % (hostname, "audio",'tts_%s.wav' % hashnumber)
    words_times_file=open(ahotts_dir+'/tts_'+hashnumber+'.wrd','r')
    words_times=words_times_file.readlines()
    words_times_file.close()
    os.remove(ahotts_dir+'/tts_'+hashnumber+'.wrd')
    os.remove(ahotts_dir+'/tts_'+hashnumber+'.pho')
    log.info(str(words))
    audio_url = "%s%s/%s" % (hostname, "audio",'tts_%s.wav' % hashnumber)
    words_times_file=open(wrdfilename,'r')
    words_times=words_times_file.readlines()
    words_times_file.close()
    os.remove(inputfilename)
    os.remove(wrdfilename)
    """

    """ Call to socket, does not work properly in docker compose environment
    # Write text to file
    inputfilename="%s/%s/tts_%s.txt" % (cwdir,tmpdir,hashnumber)
    inputfile=open(inputfilename,"wb")
    inputfile.write(input.encode('latin-1')+'\n'.encode('latin-1'))
    inputfile.close()
    # Open socket
    socketa=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    ipa=socket.gethostbyname(ahotts_server_ip)
    socketa.connect((ipa,int(ahotts_server_port)))
    # Write options
    options_struct=struct.Struct('4s 4s 4s 1024s 1024s 1024s ?')
    options_struct_packed=options_struct.pack(lang.encode('utf-8'),"".encode('utf-8'),ahotts_speed.encode('utf-8'),"".encode('utf-8'),("wav/tts_%s.pho" % hashnumber).encode('utf-8'),("wav/tts_%s.wrd" % hashnumber).encode('utf-8'),True)
    totalsent=0
    while totalsent<len(options_struct_packed):
        sent=socketa.send(options_struct_packed[totalsent:])
        if sent==0:
            raise RuntimeError("socket connection broken")
        totalsent=totalsent+sent
    # Write text file length + text file
    socket_write_filelength_file(socketa,inputfilename)
    # Read wav file
    wavfilename="%s/%s/tts_%s.wav" % (cwdir,tmpdir,hashnumber)
    wavfile=open(wavfilename,"wb")
    wavfile.write(socket_read_filelength_file(socketa))
    wavfile.close()
    # Read pho file
    socket_read_filelength_file(socketa)
    # Read wrd file
    wrdfilename="%s/%s/tts_%s.wrd" % (cwdir,tmpdir,hashnumber)
    wrdfile=open(wrdfilename,"wb")
    wrdfile.write(socket_read_filelength_file(socketa))
    wrdfile.close()
    # Close socket
    socketa.close()
    audio_url = "%s%s/%s" % (hostname, "audio",'tts_%s.wav' % hashnumber)
    words_times_file=open(wrdfilename,'r')
    words_times=words_times_file.readlines()
    words_times_file.close()
    os.remove(inputfilename)
    os.remove(wrdfilename)
    """

    response=requests.post("http://"+ahotts_server_ip+":"+ahotts_server_port+"/ahotts_getaudio",data={'text':input.encode('latin-1')+'\n'.encode('latin-1'),'lang':lang,'voice':voice,'speed':ahotts_speed})
    url="http://"+ahotts_server_ip+":"+ahotts_server_port+"/ahotts_getaudio"
    data={'text':input.encode('latin-1')+'\n'.encode('latin-1'),'lang':lang,'voice':voice,'speed':ahotts_speed}
    
    if response.status_code==200:
        files=response.json()
        wavfile=files['wav']
        wrdfile=files['wrd']
        response2=requests.get("http://"+ahotts_server_ip+":"+ahotts_server_port+"/ahotts_downloadfile?file="+wavfile)
        if response2.status_code==200:
            wavfilename="%s/%s/tts_%s.wav" % (cwdir,tmpdir,hashnumber)
            wavfile=open(wavfilename,"wb")
            for chunk in response2.iter_content(1024):
                wavfile.write(chunk)
            wavfile.close()
            response3=requests.get("http://"+ahotts_server_ip+":"+ahotts_server_port+"/ahotts_downloadfile?file="+wrdfile)
            if response3.status_code==200:
                wrdfilename="%s/%s/tts_%s.wrd" % (cwdir,tmpdir,hashnumber)
                wrdfile=open(wrdfilename,"wb")
                for chunk in response3.iter_content(1024):
                    wrdfile.write(chunk)
                wrdfile.close()
            else:
                msg = "AhoTTS server error"
                log.error(msg)
                raise VoiceException(msg)
        else:
            msg = "AhoTTS server error"
            log.error(msg)
            raise VoiceException(msg)
    else:
        msg = "AhoTTS server error"
        log.error(msg)
        raise VoiceException(msg)
    audio_url = "%s%s/%s" % (hostname, "audio",'tts_%s.wav' % hashnumber)
    words_times_file=open(wrdfilename,'r')
    words_times=words_times_file.readlines()
    words_times_file.close()
    os.remove(wrdfilename)

    words_times=list(map(lambda x:x[:-1].split(' ')[1],words_times))
    tokens = []
    starttime=0.0
    lastendtime=0.0
    for word_ind in range(len(words)):
        word=words[word_ind]
        if word_ind>len(words_times)-1:
            endtime=lastendtime
        else:
            endtime=float(words_times[word_ind])/1000
        tokens.append({"orth":word, "starttime":starttime, "endtime":endtime})
        starttime=endtime
        lastendtime=endtime
    return (audio_url, tokens)



def get_orth(utterance):
    orth_list = []
    paragraphs = utterance["paragraphs"]
    for paragraph in paragraphs:
        sentences = paragraph["sentences"]
        for sentence in sentences:
            phrases = sentence["phrases"]
            for phrase in phrases:
                tokens = phrase["tokens"]
                for token in tokens:
                    words = token["words"]
                    for word in words:
                        split_list=word["orth"].split('-')
                        split_list_initial='-'.join(split_list[:-1])
                        if (split_list_initial in specials_eu and not any(word["orth"].startswith(special_eu) for special_eu in filter(lambda x:x.startswith(split_list_initial+'-'),specials_eu))) or re.search('[^0-9\-]',word["orth"])==None:
                            orth_list.append(word["orth"])
                        else:
                            for wordpart in split_list:
                                orth_list.append(wordpart)
    return orth_list




if __name__ == "__main__":
    input = {
        "lang": "eu",
        "original_text": "test",
        "paragraphs": [
            {
                "sentences": [
                    {
                        "phrases": [
                            {
                                "tokens": [
                                    {
                                        "words": [
                                            {
                                                "orth": "test",
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }
    

    lang = "eu"
    log.log_level = "debug"

    #HB voice['name'] is used in synthesise?
    voice = {"name": "ahotts-eu-female"}
    #voice = "ahotts-eu-female"
    
    (audio_url, tokens) = synthesise(lang, voice, input)
    log.debug("AUDIO URL: %s" % audio_url)
    log.debug("TOKENS: %s" % tokens)
