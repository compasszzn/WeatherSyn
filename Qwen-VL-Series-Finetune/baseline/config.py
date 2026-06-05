chosen_stations = ['ABQ', 'AKQ', 'ALY', 'BGM', 'BOX', 'BTV', 'BUF', 'CAE', 'CAR', 'CHS', 'CLE', 'CTP', 'EKA', 'FGZ', 'GSP', 'GYX', 'HFO', 'ILM', 'ILN', 'IWX', 'LOX', 'LWX', 'MHX', 'MTR', 'OKX', 'OTX', 'PBZ', 'PHI', 'PQR', 'PSR', 'RAH', 'RLX', 'RNK', 'SEW', 'SGX', 'SJU', 'SLC', 'TFX', 'TWC', 'VEF']
final_stations = ['ABQ', 'AKQ', 'ALY', 'BGM', 'BOX', 'BTV', 'BUF', 'CAE', 'CAR', 'CLE', 'CTP', 'FGZ', 'GSP', 'GYX', 'HFO', 'ILM', 'ILN', 'LOX', 'LWX', 'MHX', 'MTR', 'OTX', 'PHI', 'PQR', 'RAH', 'RLX', 'RNK', 'SEW', 'SGX', 'TFX', 'VEF']
ERA5_SINGLE_LEVEL=['land_sea_mask','10m_u_component_of_wind','10m_v_component_of_wind','2m_temperature','mean_sea_level_pressure',
                   'sea_surface_temperature','snow_depth','surface_pressure','total_cloud_cover','total_precipitation_6hr','total_column_water_vapour',
                   'total_column_water']
AREA_MAP = {'hk':'Hong_Kong','mtr':'San_Francisco','lox':'Los_Angeles','okx':'New_York',
            'lwx':'Washington_DC','pbz':'Pittsburgh','pqr':'Portland',
            'sew':'Seattle','box':"Boston",'vef':"Las_Vegas"}
ERA5_PRESSURE_LEVEL=['geopotential','specific_humidity','temperature','u_component_of_wind','v_component_of_wind','vertical_velocity']
PRESSURE_LEVELS = [200,500,700, 850]
ERA5_PRESSURE_LIST=['geopotential-200','geopotential-500','geopotential-700','geopotential-850',
                    'specific_humidity-200','specific_humidity-500','specific_humidity-700','specific_humidity-850',
                    'temperature-200','temperature-500','temperature-700','temperature-850',
                    'u_component_of_wind-200','u_component_of_wind-500','u_component_of_wind-700','u_component_of_wind-850',
                    'v_component_of_wind-200','v_component_of_wind-500','v_component_of_wind-700','v_component_of_wind-850',]
DESCRIPTION={
    'land_sea_mask':'This image refers the proportion of land, as opposed to ocean or inland waters',
    '10m_u_component_of_wind':'This image refers to the eastward component of the 10m wind. It is the horizontal speed of air moving towards the east, at a height of ten metres above the surface of the Earth',
    '10m_v_component_of_wind':'This image refers to the northward component of the 10m wind. It is the horizontal speed of air moving towards the north, at a height of ten metres above the surface of the Earth',
    '2m_temperature':'This image refers to the temperature of air at 2m above the surface of land, sea or in-land waters.',
    'mean_sea_level_pressure':'This image refers to the pressure of the atmosphere adjusted to the height of mean sea level.',
    'sea_surface_temperature':"This image refers to the temperature of sea water near the surface.",
    'snow_depth':'This image refers to the depth of snow from the snow-covered area.',
    'surface_pressure':'This parameter is the pressure of the atmosphere on the surface of land, sea and in-land water.',
    'total_cloud_cover':'This parameter is the proportion of a grid box area covered by cloud.',
    'total_precipitation_6hr':'This image refers to the total precipitation over the past 6 hours',
    'total_column_water_vapour':'This image refers to the total amount of water vapour in a vertical column of the atmosphere, from the surface to the top of the atmosphere',
    'total_column_water':'This image refers to the total amount of liquid water in a vertical column of the atmosphere',
    'geopotential-200':'The following four images refers to the geopotential height at the 200 hPa, 500, 700 and 850 hPa pressure level respectively, which can be used to identify weather systems such as cyclones, anticyclones, troughs and ridges.',
    # 'geopotential-500':'This image refers to the geopotential height at the 500 hPa pressure level, which can be used to identify weather systems such as cyclones, anticyclones, troughs and ridges.',
    # 'geopotential-700':'This image refers to the geopotential height at the 700 hPa pressure level, which can be used to identify weather systems such as cyclones, anticyclones, troughs and ridges.',
    # 'geopotential-850':'This image refers to the geopotential height at the 850 hPa pressure level, which can be used to identify weather systems such as cyclones, anticyclones, troughs and ridges.',
    'specific_humidity-200':'The following four images refer to the mass of water vapour per kilogram of moist air 200 hPa, 500, 700 and 850 hPa pressure level respectively.',
    # 'specific_humidity-500':'This image refers to the mass of water vapour per kilogram of moist air at the 500 hPa pressure level.',
    # 'specific_humidity-700':'This image refers to the mass of water vapour per kilogram of moist air at the 700 hPa pressure level.',
    # 'specific_humidity-850':'This image refers to the mass of water vapour per kilogram of moist air at the 850 hPa pressure level.',
    'temperature-200':'The following four images refer to the temperature in the atmosphere at the 200 hPa, 500, 700 and 850 hPa pressure level respectively.',
    # 'temperature-500':'This image refers to the temperature in the atmosphere at the 500 hPa pressure level.',
    # 'temperature-700':'This image refers to the temperature in the atmosphere at the 700 hPa pressure level.',
    # 'temperature-850':'This image refers to the temperature in the atmosphere at the 850 hPa pressure level.',
    'u_component_of_wind-200':'The following four images refer to the eastward component of the wind at the 200 hPa, 500, 700 and 850 hPa pressure level respectively. It is the horizontal speed of air moving towards the east.',
    # 'u_component_of_wind-500':'This image refers to the eastward component of the wind at the 500 hPa pressure level. It is the horizontal speed of air moving towards the east.',
    # 'u_component_of_wind-700':'This image refers to the eastward component of the wind at the 700 hPa pressure level. It is the horizontal speed of air moving towards the east.',
    # 'u_component_of_wind-850':'This image refers to the eastward component of the wind at the 850 hPa pressure level. It is the horizontal speed of air moving towards the east.',
    'v_component_of_wind-200':'The following four images refer to the northward component of the wind at the 200 hPa, 500, 700 and 850 hPa pressure level respectively. It is the horizontal speed of air moving towards the north.',
    # 'v_component_of_wind-500':'This image refers to the northward component of the wind at the 500 hPa pressure level. It is the horizontal speed of air moving towards the north.',
    # 'v_component_of_wind-700':'This image refers to the northward component of the wind at the 700 hPa pressure level. It is the horizontal speed of air moving towards the north.',
    # 'v_component_of_wind-850':'This image refers to the northward component of the wind at the 850 hPa pressure level. It is the horizontal speed of air moving towards the north.',
}
AREA_MAP = {'hk':'Hong_Kong','mtr':'San_Francisco','lox':'Los_Angeles','okx':'New_York',
            'lwx':'Washington_DC','pbz':'Pittsburgh','pqr':'Portland',
            'sew':'Seattle','box':"Boston",'vef':"Las_Vegas"}
AREA_NAME_MAP = {'hk':'Hong Kong','mtr':'San Francisco','lox':'Los Angeles','okx':'New York',
            'lwx':'Washington DC','pbz':'Pittsburgh','pqr':'Portland',
            'sew':'Seattle','box':"Boston",'vef':"Las Vegas"}
AREA_BOUNDS = {
    'Hong_Kong': {'lat_min': 20.5, 'lat_max': 24.5, 'lon_min': 112, 'lon_max': 116},
    'San_Francisco': {'lat_min': 34, 'lat_max': 41, 'lon_min': 234.8, 'lon_max': 246},
    'Los_Angeles': {'lat_min': 33.0, 'lat_max': 37, 'lon_min': 238, 'lon_max': 246.0},
    'New_York': {'lat_min': 36, 'lat_max': 48.4, 'lon_min': 275.4, 'lon_max': 290.4},
    'Pittsburgh': {'lat_min': 35, 'lat_max': 43, 'lon_min': 272, 'lon_max': 284},
    'Portland':{'lat_min': 40.5, 'lat_max': 50, 'lon_min': 234, 'lon_max': 242},
    'Washington_DC':{'lat_min': 34, 'lat_max': 46, 'lon_min': 268, 'lon_max': 290},
    'Seattle':{'lat_min': 41, 'lat_max': 50, 'lon_min': 235, 'lon_max': 241},
    'Las_Vegas':{'lat_min': 32, 'lat_max': 41, 'lon_min': 239, 'lon_max': 250},
    'Boston':{'lat_min': 40, 'lat_max': 47, 'lon_min': 282, 'lon_max': 298},
    'America':{'lat_min': 20,'lat_max': 70,'lon_min': 210,'lon_max': 310},
    'China': {'lat_min': 10,'lat_max': 40,'lon_min': 80,'lon_max': 140}
}
stations = {
    "ABQ": "Albuquerque, New Mexico",
    "ABR": "Aberdeen, South Dakota",
    "AFC": "Anchorage, Alaska",
    "AFG": "Fairbanks, Alaska",
    "AJK": "Juneau, Alaska",
    "AKQ": "Wakefield, Virginia",
    "ALY": "Albany, New York",
    "AMA": "Amarillo, Texas",
    "APX": "Gaylord, Michigan",
    "ARX": "La Crosse, Wisconsin",
    "BGM": "Binghamton, New York",
    "BIS": "Bismarck, North Dakota",
    "BMX": "Birmingham, Alabama",
    "BOI": "Boise, Idaho",
    "BOU": "Denver/Boulder, Colorado",
    "BOX": "Boston, Massachusetts",
    "BRO": "Brownsville, Texas",
    "BTV": "Burlington, Vermont",
    "BUF": "Buffalo, New York",
    "BYZ": "Billings, Montana",
    "CAE": "Columbia, South Carolina",
    "CAR": "Caribou, Maine",
    "CHS": "Charleston, South Carolina",
    "CLE": "Cleveland, Ohio",
    "CRP": "Corpus Christi, Texas",
    "CTP": "State College, Pennsylvania",
    "CYS": "Cheyenne, Wyoming",
    "DDC": "Dodge City, Kansas",
    "DLH": "Duluth, Minnesota",
    "DMX": "Des Moines, Iowa",
    "DTX": "Detroit/Pontiac, Michigan",
    "EAX": "Kansas City/Pleasant Hill, Missouri",
    "EKA": "Eureka, California",
    "EWX": "Austin/San Antonio, Texas",
    "FFC": "Atlanta, Georgia",
    "FGF": "Grand Forks, North Dakota",
    "FGZ": "Flagstaff, Arizona",
    "FSD": "Sioux Falls, South Dakota",
    "FWD": "Dallas/Fort Worth, Texas",
    "GGW": "Glasgow, Montana",
    "GID": "Hastings, Nebraska",
    "GJT": "Grand Junction, Colorado",
    "GLD": "Goodland, Kansas",
    "GRB": "Green Bay, Wisconsin",
    "GRR": "Grand Rapids, Michigan",
    "GSP": "Greer, South Carolina",
    "GUM": "Tiyan, Guam",
    "GYX": "Portland, Maine",
    "HFO": "Honolulu, Hawaii",
    "HGX": "Houston/Galveston, Texas",
    "HUN": "Huntsville, Alabama",
    "ICT": "Wichita, Kansas",
    "ILM": "Wilmington, North Carolina",
    "ILN": "Wilmington, Ohio",
    "ILX": "Central Illinois",
    "IND": "Indianapolis, Indiana",
    "IWX": "Northern Indiana",
    "JAN": "Jackson, Mississippi",
    "JAX": "Jacksonville, Florida",
    "JKL": "Jackson, Kentucky",
    "KEY": "Key West, Florida",
    "LBF": "North Platte, Nebraska",
    "LCH": "Lake Charles, Louisiana",
    "LIX": "New Orleans/Baton Rouge, Louisiana",
    "LKN": "Elko, Nevada",
    "LMK": "Louisville, Kentucky",
    "LOT": "Chicago, Illinois",
    "LOX": "Los Angeles, California",
    "LSX": "St. Louis, Missouri",
    "LWX": "Sterling, Virginia",
    "LZK": "Little Rock, Arkansas",
    "MAF": "Midland/Odessa, Texas",
    "MEG": "Memphis, Tennessee",
    "MFL": "Miami, Florida",
    "MFR": "Medford, Oregon",
    "MHX": "Newport/Morehead, North Carolina",
    "MKX": "Milwaukee/Sullivan, Wisconsin",
    "MLB": "Melbourne, Florida",
    "MOB": "Mobile, Alabama",
    "MQT": "Marquette, Michigan",
    "MSO": "Missoula, Montana",
    "MTR": "San Francisco Bay Area, California",
    "OAX": "Omaha/Valley, Nebraska",
    "OHX": "Nashville, Tennessee",
    "OKX": "Upton, New York",
    "OTX": "Spokane, Washington",
    "OUN": "Oklahoma City, Oklahoma",
    "PAH": "Paducah, Kentucky",
    "PBZ": "Pittsburgh, Pennsylvania",
    "PDT": "Pendleton, Oregon",
    "PHI": "Mt. Holly, New Jersey",
    "PIH": "Pocatello, Idaho",
    "PPG": "Pago Pago",
    "PQR": "Portland, Oregon",
    "PSR": "Phoenix, Arizona",
    "PUB": "Pueblo, Colorado",
    "RAH": "Raleigh/Durham, North Carolina",
    "REV": "Reno, Nevada",
    "RIW": "Riverton, Wyoming",
    "RLX": "Charleston, West Virginia",
    "RNK": "Blacksburg, Virginia",
    "SEW": "Seattle/Tacoma, Washington",
    "SGF": "Springfield, Missouri",
    "SGX": "San Diego, California",
    "SHV": "Shreveport, Louisiana",
    "SJT": "San Angelo, Texas",
    "SJU": "San Juan, Puerto Rico",
    "SLC": "Salt Lake City, Utah",
    "STO": "Sacramento, California",
    "TBW": "Tampa Bay Area, Florida",
    "TFX": "Great Falls, Montana",
    "TOP": "Topeka, Kansas",
    "TSA": "Tulsa, Oklahoma",
    "TWC": "Tucson, Arizona",
    "UNR": "Rapid City, South Dakota",
    "VEF": "Las Vegas, Nevada",
}

station_coords = {
    "ABQ": [
        35.0841034,
        -106.650985
    ],
    "ABR": [
        45.4649805,
        -98.487813
    ],
    "AFC": [
        61.2163129,
        -149.894852
    ],
    "AFG": [
        64.837845,
        -147.716675
    ],
    "AJK": [
        58.3019613,
        -134.4196751
    ],
    "AKQ": [
        38.8245735,
        -77.2402667
    ],
    "ALY": [
        42.6511674,
        -73.754968
    ],
    "AMA": [
        35.20729,
        -101.8371192
    ],
    "APX": [
        45.027513,
        -84.674752
    ],
    "ARX": [
        43.8122836,
        -91.2514355
    ],
    "BGM": [
        42.098698,
        -75.9125187
    ],
    "BIS": [
        46.808327,
        -100.783739
    ],
    "BMX": [
        33.5206824,
        -86.8024326
    ],
    "BOI": [
        43.6166163,
        -116.200886
    ],
    "BOU": [
        39.9852484,
        -105.2319268
    ],
    "BOX": [
        42.3554334,
        -71.060511
    ],
    "BRO": [
        25.9024289,
        -97.4981698
    ],
    "BTV": [
        44.4761601,
        -73.212906
    ],
    "BUF": [
        42.8867166,
        -78.8783922
    ],
    "BYZ": [
        45.7874957,
        -108.49607
    ],
    "CAE": [
        34.000754,
        -81.0352313
    ],
    "CAR": [
        46.8606301,
        -68.0116807
    ],
    "CHS": [
        32.7884363,
        -79.9399309
    ],
    "CLE": [
        41.4996574,
        -81.6936772
    ],
    "CRP": [
        27.7635302,
        -97.4033191
    ],
    "CTP": [
        40.7944504,
        -77.8616386
    ],
    "CYS": [
        41.139981,
        -104.820246
    ],
    "DDC": [
        37.7527982,
        -100.0170787
    ],
    "DLH": [
        46.7838287,
        -92.1052679
    ],
    "DMX": [
        41.5868654,
        -93.6249494
    ],
    "DTX": [
        42.6073046,
        -83.2508029
    ],
    "EAX": [
        38.809957,
        -94.2642173
    ],
    "EKA": [
        40.8018746,
        -124.1707558
    ],
    "EWX": [
        29.5482186,
        -98.5276176
    ],
    "FFC": [
        33.7544657,
        -84.3898151
    ],
    "FGF": [
        47.9252104,
        -97.0306325
    ],
    "FGZ": [
        35.1987522,
        -111.651822
    ],
    "FSD": [
        43.5476008,
        -96.7293629
    ],
    "FWD": [
        32.8370525,
        -97.0339395
    ],
    "GGW": [
        48.1955915,
        -106.635556
    ],
    "GID": [
        40.5861322,
        -98.3898883
    ],
    "GJT": [
        39.0672568,
        -108.56448
    ],
    "GLD": [
        39.350833,
        -101.710172
    ],
    "GRB": [
        44.5126379,
        -88.0125794
    ],
    "GRR": [
        42.9632425,
        -85.6678639
    ],
    "GSP": [
        34.9381361,
        -82.2272119
    ],
    "GUM": [
        13.4972084,
        144.8154958
    ],
    "GYX": [
        43.6573605,
        -70.2586618
    ],
    "HFO": [
        21.304547,
        -157.855676
    ],
    "HGX": [
        29.6045119,
        -95.1778052
    ],
    "HUN": [
        34.729847,
        -86.5859011
    ],
    "ICT": [
        37.6922361,
        -97.3375448
    ],
    "ILM": [
        34.2352853,
        -77.9487284
    ],
    "ILN": [
        39.4453393,
        -83.8285375
    ],
    "ILX": [
        41.8873357,
        -87.7653497
    ],
    "IND": [
        39.7683331,
        -86.1583502
    ],
    "IWX": [
        41.6153932,
        -87.5212764
    ],
    "JAN": [
        32.2998686,
        -90.1830408
    ],
    "JAX": [
        30.3321838,
        -81.655651
    ],
    "JKL": [
        37.4200233,
        -83.9913882
    ],
    "KEY": [
        24.5548262,
        -81.8020722
    ],
    "LBF": [
        41.1368333,
        -100.7612819
    ],
    "LCH": [
        30.2305095,
        -93.2169807
    ],
    "LIX": [
        30.3371748,
        -89.8252735
    ],
    "LKN": [
        41.1958128,
        -115.3272864
    ],
    "LMK": [
        38.2542376,
        -85.759407
    ],
    "LOT": [
        41.8755616,
        -87.6244212
    ],
    "LOX": [
        34.0536909,
        -118.242766
    ],
    "LSX": [
        38.6280278,
        -90.1910154
    ],
    "LWX": [
        39.003685,
        -77.4083096
    ],
    "LZK": [
        34.7465071,
        -92.2896267
    ],
    "MAF": [
        31.938462,
        -102.2768668
    ],
    "MEG": [
        35.1460249,
        -90.0517638
    ],
    "MFL": [
        25.7741728,
        -80.19362
    ],
    "MFR": [
        42.3264181,
        -122.8718605
    ],
    "MHX": [
        34.7765375,
        -76.8766524
    ],
    "MKX": [
        42.9679419,
        -88.5491595
    ],
    "MLB": [
        28.0785034,
        -80.6077908
    ],
    "MOB": [
        30.6913462,
        -88.0437509
    ],
    "MQT": [
        46.4481521,
        -87.6305899
    ],
    "MSO": [
        46.8701049,
        -113.995267
    ],
    "MTR": [
        37.7884969,
        -122.3558473
    ],
    "OAX": [
        42.2905411,
        -96.4821405
    ],
    "OHX": [
        36.1622767,
        -86.7742984
    ],
    "OKX": [
        40.869543,
        -72.8867697
    ],
    "OTX": [
        47.6571934,
        -117.42351
    ],
    "OUN": [
        35.4729886,
        -97.5170536
    ],
    "PAH": [
        37.0833893,
        -88.6000478
    ],
    "PBZ": [
        40.4416941,
        -79.9900861
    ],
    "PDT": [
        45.672075,
        -118.7885967
    ],
    "PHI": [
        39.9928898,
        -74.7876624
    ],
    "PIH": [
        42.8620287,
        -112.450627
    ],
    "PPG": [
        -14.2754786,
        -170.7048298
    ],
    "PQR": [
        45.5202471,
        -122.674194
    ],
    "PSR": [
        33.4484367,
        -112.074141
    ],
    "PUB": [
        38.263995,
        -104.6141867
    ],
    "RAH": [
        35.8803614,
        -78.7872382
    ],
    "REV": [
        39.5261788,
        -119.812658
    ],
    "RIW": [
        43.0247245,
        -108.380727
    ],
    "RLX": [
        38.3505995,
        -81.6332812
    ],
    "RNK": [
        37.2296566,
        -80.4136767
    ],
    "SEW": [
        47.4475673,
        -122.3080159
    ],
    "SGF": [
        37.2081729,
        -93.2922715
    ],
    "SGX": [
        32.7174202,
        -117.162772
    ],
    "SHV": [
        32.5135356,
        -93.7477839
    ],
    "SJT": [
        31.4649685,
        -100.4405094
    ],
    "SJU": [
        18.384239,
        -66.05344
    ],
    "SLC": [
        40.7596198,
        -111.886797
    ],
    "STO": [
        38.5810606,
        -121.493895
    ],
    "TBW": [
        27.8979917,
        -82.5190645
    ],
    "TFX": [
        47.5048851,
        -111.29189
    ],
    "TOP": [
        39.049011,
        -95.677556
    ],
    "TSA": [
        36.1563122,
        -95.9927516
    ],
    "TWC": [
        32.2228765,
        -110.974847
    ],
    "UNR": [
        44.0806041,
        -103.228023
    ],
    "VEF": [
        36.1674263,
        -115.1484131
    ]
}
station_thresholds = {
    'ABQ': 0.8,
    'AKQ': 0.98,#
    'ALY': 0.7,
    'BGM': 0.83,
    'BOX': 0.77,
    'BTV': 0.8,
    'BUF': 0.80,
    'CAE': 0.83,        
    'CAR': 0.98,#
    'CHS': 0.98,#
    'CLE': 0.98,#
    'CTP': 0.75,
    'EKA': 0.95,
    'FGZ': 0.95,
    'GSP': 0.9,
    'GYX': 0.72,
    'HFO': 0.8,#
    'ILM': 0.84,
    'ILN': 0.75,
    'IWX': 0.98,#
    'LOX': 0.70,#
    'LWX': 0.95,#
    'MHX': 0.98,
    'MTR': 0.85,
    'OKX': 0.98,
    'OTX': 0.9,
    'PBZ': 0.87,
    'PHI': 0.95,
    'PQR': 0.75,
    'PSR': 0.95,
    'RAH': 0.85,
    'RLX': 0.9,
    'RNK': 0.75,
    'SEW': 0.70,
    'SGX': 0.68,
    'SJU': 0.95,
    'SLC': 0.98,
    'TFX': 0.8,
    'TWC': 0.98,
    'VEF': 0.85
}

