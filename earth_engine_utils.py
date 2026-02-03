import ee
import json
import tempfile
import os

def initialize_earth_engine(credentials_path):
    """Initialize Earth Engine with service account credentials"""
    try:
        # Validate credentials file exists and is readable
        if not os.path.exists(credentials_path):
            print(f"Credentials file not found: {credentials_path}")
            return False
            
        # Read and validate the service account credentials JSON
        with open(credentials_path, 'r') as f:
            key_data = json.load(f)
        
        # Validate required fields in the JSON
        required_fields = ['client_email', 'private_key', 'project_id']
        for field in required_fields:
            if field not in key_data:
                print(f"Missing required field in credentials: {field}")
                return False
        
        # Extract service account email
        service_account_email = key_data['client_email']
        project_id = key_data.get('project_id', None)
        
        print(f"Attempting to authenticate with service account: {service_account_email}")
        
        # Create service account credentials
        credentials = ee.ServiceAccountCredentials(service_account_email, credentials_path)
        
        # Initialize Earth Engine with project if available
        if project_id:
            ee.Initialize(credentials, project=project_id)
        else:
            ee.Initialize(credentials)
        
        # Test the connection with a simple operation
        try:
            test_result = ee.Number(42).getInfo()
            print(f"Earth Engine connection test successful: {test_result}")
        except Exception as test_error:
            print(f"Connection test failed: {str(test_error)}")
            return False
        
        print("✅ Earth Engine initialized successfully!")
        return True
        
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in credentials file: {str(e)}")
        return False
    except FileNotFoundError:
        print(f"Credentials file not found: {credentials_path}")
        return False
    except Exception as e:
        print(f"Error initializing Earth Engine: {str(e)}")
        # Check for common error patterns
        error_str = str(e).lower()
        if 'invalid_grant' in error_str:
            print("Hint: This error usually means your service account key has expired.")
            print("Please generate a new service account key from the Google Cloud Console.")
        elif 'project not registered' in error_str:
            print("Hint: Your Google Cloud project may not be registered with Earth Engine.")
            print("Please register your project at https://signup.earthengine.google.com/")
        return False

# FAO GAUL Dataset references
def get_fao_collections():
    """Get FAO GAUL collections"""
    try:
        FAO_GAUL = ee.FeatureCollection("FAO/GAUL/2015/level0")  # Countries
        FAO_GAUL_ADMIN1 = ee.FeatureCollection("FAO/GAUL/2015/level1")  # Admin1 (states/provinces)
        FAO_GAUL_ADMIN2 = ee.FeatureCollection("FAO/GAUL/2015/level2")  # Admin2 (municipalities)
        return FAO_GAUL, FAO_GAUL_ADMIN1, FAO_GAUL_ADMIN2
    except Exception as e:
        print(f"Error loading FAO collections: {str(e)}")
        return None, None, None

def get_admin_boundaries(level, country_code=None, admin1_code=None):
    """Get administrative boundaries at different levels"""
    try:
        FAO_GAUL, FAO_GAUL_ADMIN1, FAO_GAUL_ADMIN2 = get_fao_collections()
        
        if level == 0:  # Countries
            return FAO_GAUL
        elif level == 1:  # Admin1 (states/provinces)
            if country_code and FAO_GAUL_ADMIN1:
                return FAO_GAUL_ADMIN1.filter(ee.Filter.eq('ADM0_CODE', country_code))
            return FAO_GAUL_ADMIN1
        elif level == 2:  # Admin2 (municipalities)
            if admin1_code and FAO_GAUL_ADMIN2:
                return FAO_GAUL_ADMIN2.filter(ee.Filter.eq('ADM1_CODE', admin1_code))
            return FAO_GAUL_ADMIN2
        return None
    except Exception as e:
        print(f"Error getting admin boundaries: {str(e)}")
        return None

def get_boundary_names(fc, level):
    """Get names of boundaries in a feature collection for a specific level"""
    try:
        if fc is None:
            return []
            
        if level == 0:  # Countries
            names = fc.aggregate_array('ADM0_NAME').getInfo()
        elif level == 1:  # Admin1 (states/provinces)
            names = fc.aggregate_array('ADM1_NAME').getInfo()
        elif level == 2:  # Admin2 (municipalities)
            names = fc.aggregate_array('ADM2_NAME').getInfo()
        else:
            names = []
        
        # Filter out None values and return sorted unique list
        names = [name for name in names if name is not None]
        return sorted(list(set(names)))  # Remove duplicates and sort
        
    except Exception as e:
        print(f"Error getting boundary names: {str(e)}")
        return []
