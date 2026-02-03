import ee

def mask_clouds(image):
    """Mask clouds and cirrus for Sentinel-2 images"""
    qa = image.select('QA60')
    cloud_mask = qa.bitwiseAnd(1 << 10).eq(0)
    cirrus_mask = qa.bitwiseAnd(1 << 11).eq(0)
    return image.updateMask(cloud_mask.And(cirrus_mask))

def add_vegetation_indices(image):
    """Add all vegetation indices to the image"""
    
    # NDVI - Normalized Difference Vegetation Index
    ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
    
    # ARVI - Atmospherically Resistant Vegetation Index
    arvi = image.expression(
        '(NIR - (2 * RED - BLUE)) / (NIR + (2 * RED - BLUE))', {
            'NIR': image.select('B8'),
            'RED': image.select('B4'),
            'BLUE': image.select('B2')
        }).rename('ARVI')
    
    # ATSAVI - Adjusted Transformed Soil-Adjusted Vegetation Index
    atsavi = image.expression(
        'a * (NIR - a * RED - b) / (a * NIR + RED - a * b + X * (1 + a * a))', {
            'NIR': image.select('B8'),
            'RED': image.select('B4'),
            'a': 1.22,
            'b': 0.03,
            'X': 0.08
        }).rename('ATSAVI')
    
    # DVI - Difference Vegetation Index
    dvi = image.expression('NIR - RED', {
        'NIR': image.select('B8'),
        'RED': image.select('B4')
    }).rename('DVI')
    
    # EVI - Enhanced Vegetation Index
    evi = image.expression(
        '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))', {
            'NIR': image.select('B8'),
            'RED': image.select('B4'),
            'BLUE': image.select('B2')
        }).rename('EVI')
    
    # EVI2 - Two-band Enhanced Vegetation Index
    evi2 = image.expression(
        '2.5 * (NIR - RED) / (NIR + 2.4 * RED + 1)', {
            'NIR': image.select('B8'),
            'RED': image.select('B4')
        }).rename('EVI2')
    
    # GNDVI - Green Normalized Difference Vegetation Index
    gndvi = image.normalizedDifference(['B8', 'B3']).rename('GNDVI')
    
    # MSAVI - Modified Soil-Adjusted Vegetation Index
    msavi = image.expression(
        '(2 * NIR + 1 - sqrt((2 * NIR + 1)**2 - 8 * (NIR - RED))) / 2', {
            'NIR': image.select('B8'),
            'RED': image.select('B4')
        }).rename('MSAVI')
    
    # MSI - Moisture Stress Index
    msi = image.expression('SWIR1 / NIR', {
        'SWIR1': image.select('B11'),
        'NIR': image.select('B8')
    }).rename('MSI')
    
    # MTVI - Modified Triangular Vegetation Index
    mtvi = image.expression(
        '1.2 * (1.2 * (NIR - GREEN) - 2.5 * (RED - GREEN))', {
            'NIR': image.select('B8'),
            'RED': image.select('B4'),
            'GREEN': image.select('B3')
        }).rename('MTVI')
    
    # MTVI2 - Modified Triangular Vegetation Index 2
    mtvi2 = image.expression(
        '(1.5 * (1.2 * (NIR - GREEN) - 2.5 * (RED - GREEN)) / ' +
        'sqrt((2 * NIR + 1)**2 - (6 * NIR - 5 * sqrt(RED)) - 0.5))', {
            'NIR': image.select('B8'),
            'RED': image.select('B4'),
            'GREEN': image.select('B3')
        }).rename('MTVI2')
    
    # NDTI - Normalized Difference Tillage Index
    ndti = image.normalizedDifference(['B11', 'B12']).rename('NDTI')
    
    # NDWI - Normalized Difference Water Index
    ndwi = image.normalizedDifference(['B3', 'B8']).rename('NDWI')
    
    # OSAVI - Optimized Soil-Adjusted Vegetation Index
    osavi = image.expression('(NIR - RED) / (NIR + RED + 0.16)', {
        'NIR': image.select('B8'),
        'RED': image.select('B4')
    }).rename('OSAVI')
    
    # RDVI - Renormalized Difference Vegetation Index
    rdvi = image.expression('(NIR - RED) / sqrt(NIR + RED)', {
        'NIR': image.select('B8'),
        'RED': image.select('B4')
    }).rename('RDVI')
    
    # RI - Redness Index
    ri = image.expression('RED / GREEN', {
        'RED': image.select('B4'),
        'GREEN': image.select('B3')
    }).rename('RI')
    
    # RVI - Ratio Vegetation Index
    rvi = image.expression('NIR / RED', {
        'NIR': image.select('B8'),
        'RED': image.select('B4')
    }).rename('RVI')
    
    # SAVI - Soil-Adjusted Vegetation Index
    savi = image.expression('1.5 * (NIR - RED) / (NIR + RED + 0.5)', {
        'NIR': image.select('B8'),
        'RED': image.select('B4')
    }).rename('SAVI')
    
    # TVI - Triangular Vegetation Index
    tvi = image.expression('0.5 * (120 * (NIR - GREEN) - 200 * (RED - GREEN))', {
        'NIR': image.select('B8'),
        'RED': image.select('B4'),
        'GREEN': image.select('B3')
    }).rename('TVI')
    
    # TSAVI - Transformed Soil-Adjusted Vegetation Index
    tsavi = image.expression(
        '(a * (NIR - a * RED - b)) / (RED + a * (NIR - b) + X * (1 + a * a))', {
            'NIR': image.select('B8'),
            'RED': image.select('B4'),
            'a': 1.22,
            'b': 0.03,
            'X': 0.08
        }).rename('TSAVI')
    
    # VARI - Visible Atmospherically Resistant Index
    vari = image.expression('(GREEN - RED) / (GREEN + RED - BLUE)', {
        'GREEN': image.select('B3'),
        'RED': image.select('B4'),
        'BLUE': image.select('B2')
    }).rename('VARI')
    
    # VIN - Vegetation Index based on NIR and Red
    vin = image.expression('NIR - RED', {
        'NIR': image.select('B8'),
        'RED': image.select('B4')
    }).rename('VIN')
    
    # WDRVI - Wide Dynamic Range Vegetation Index
    wdrvi = image.expression('(0.1 * NIR - RED) / (0.1 * NIR + RED)', {
        'NIR': image.select('B8'),
        'RED': image.select('B4')
    }).rename('WDRVI')
    
    # GCVI - Green Chlorophyll Vegetation Index
    gcvi = image.expression('(NIR / GREEN) - 1', {
        'NIR': image.select('B8'),
        'GREEN': image.select('B3')
    }).rename('GCVI')
    
    # AWEI - Automated Water Extraction Index
    aweinsh = image.expression('4 * (GREEN - SWIR1) - (0.25 * NIR + 2.75 * SWIR2)', {
        'GREEN': image.select('B3'),
        'SWIR1': image.select('B11'),
        'NIR': image.select('B8'),
        'SWIR2': image.select('B12')
    }).rename('AWEI')
    
    # MNDWI - Modified Normalized Difference Water Index
    mndwi = image.normalizedDifference(['B3', 'B11']).rename('MNDWI')
    
    # WI - Water Index
    wi = image.expression('GREEN / NIR', {
        'GREEN': image.select('B3'),
        'NIR': image.select('B8')
    }).rename('WI')
    
    # ANDWI - Automated Water Extraction Index with no shadows
    andwi = image.expression('(GREEN + 2.5 * RED - 1.5 * (NIR + SWIR1) - 0.25 * SWIR2)', {
        'GREEN': image.select('B3'),
        'RED': image.select('B4'),
        'NIR': image.select('B8'),
        'SWIR1': image.select('B11'),
        'SWIR2': image.select('B12')
    }).rename('ANDWI')
    
    # NDSI - Normalized Difference Snow Index
    ndsi = image.normalizedDifference(['B3', 'B11']).rename('NDSI')
    
    # nDDI - Normalized Difference Drought Index
    nddi = image.expression('(NDVI - NDWI) / (NDVI + NDWI)', {
        'NDVI': ndvi,
        'NDWI': ndwi
    }).rename('nDDI')
    
    # NBR - Normalized Burn Ratio
    nbr = image.normalizedDifference(['B8', 'B12']).rename('NBR')
    
    # DBSI - Dry Bareness Soil Index
    dbsi = image.expression('(SWIR1 - NIR) / (SWIR1 + NIR)', {
        'SWIR1': image.select('B11'),
        'NIR': image.select('B8')
    }).rename('DBSI')
    
    # SI - Salinity Index
    si = image.expression('(BLUE * RED)**0.5', {
        'BLUE': image.select('B2'),
        'RED': image.select('B4')
    }).rename('SI')
    
    # S3 - Salinity Index 3
    s3 = image.expression('(RED * SWIR1)**0.5', {
        'RED': image.select('B4'),
        'SWIR1': image.select('B11')
    }).rename('S3')
    
    # BRI - Brightness Index
    bri = image.expression('(RED * GREEN)**0.5', {
        'RED': image.select('B4'),
        'GREEN': image.select('B3')
    }).rename('BRI')
    
    # SSI - Soil Salinity Index
    ssi = image.expression('(SWIR1 / RED)', {
        'SWIR1': image.select('B11'),
        'RED': image.select('B4')
    }).rename('SSI')
    
    # NDSI_Salinity - Normalized Difference Salinity Index
    ndsi_salinity = image.normalizedDifference(['B3', 'B11']).rename('NDSI_Salinity')
    
    # SRPI - Simple Ratio Pigment Index
    srpi = image.expression('RED / BLUE', {
        'RED': image.select('B4'),
        'BLUE': image.select('B2')
    }).rename('SRPI')
    
    # MCARI - Modified Chlorophyll Absorption in Reflectance Index
    mcari = image.expression(
        '((RE1 - RED) - 0.2 * (RE1 - GREEN)) * (RE1 / RED)', {
            'RE1': image.select('B5'),
            'RED': image.select('B4'),
            'GREEN': image.select('B3')
        }).rename('MCARI')
    
    # NDCI - Normalized Difference Chlorophyll Index
    ndci = image.normalizedDifference(['B5', 'B4']).rename('NDCI')
    
    # PSSRb1 - Pigment Specific Simple Ratio (Chlorophyll b)
    pssrb1 = image.expression('NIR / GREEN', {
        'NIR': image.select('B8'),
        'GREEN': image.select('B3')
    }).rename('PSSRb1')
    
    # SIPI - Structure Intensive Pigment Index
    sipi = image.expression('(NIR - BLUE) / (NIR - RED)', {
        'NIR': image.select('B8'),
        'BLUE': image.select('B2'),
        'RED': image.select('B4')
    }).rename('SIPI')
    
    # PSRI - Plant Senescence Reflectance Index
    psri = image.expression('(RED - BLUE) / RE2', {
        'RED': image.select('B4'),
        'BLUE': image.select('B2'),
        'RE2': image.select('B6')
    }).rename('PSRI')
    
    # Chl_red_edge - Chlorophyll Red Edge Index
    chl_red_edge = image.expression('NIR / RE1 - 1', {
        'NIR': image.select('B8'),
        'RE1': image.select('B5')
    }).rename('Chl_red_edge')
    
    # MARI - Modified Anthocyanin Reflectance Index
    mari = image.expression('(1 / GREEN) - (1 / RE1)', {
        'GREEN': image.select('B3'),
        'RE1': image.select('B5')
    }).rename('MARI')
    
    # NDMI - Normalized Difference Moisture Index
    ndmi = image.normalizedDifference(['B8', 'B11']).rename('NDMI')
    
    # Add all indices to the image
    return image.addBands([
        ndvi, arvi, atsavi, dvi, evi, evi2, gndvi, msavi, msi, mtvi, mtvi2,
        ndti, ndwi, osavi, rdvi, ri, rvi, savi, tvi, tsavi, vari, vin, wdrvi,
        gcvi, aweinsh, mndwi, wi, andwi, ndsi, nddi, nbr, dbsi, si, s3, bri,
        ssi, ndsi_salinity, srpi, mcari, ndci, pssrb1, sipi, psri, chl_red_edge, mari, ndmi
    ])
