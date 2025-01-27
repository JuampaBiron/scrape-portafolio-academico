# api_client.py
import requests
import base64
import json
import urllib.parse
from typing import Dict, Any

class APIClient:    
    def __init__(self):
        None

    def _decode_response(self, encoded_text: str) -> Dict[str, Any]:
        """Decodifica la respuesta de la API"""
        try:
            reversed_str = encoded_text[::-1]
            decoded_bytes = base64.b64decode(reversed_str)
            decoded_str = decoded_bytes.decode('utf-8')
            result = json.loads(urllib.parse.unquote(decoded_str))
            return result
        except Exception as e:
            print(f"Error decodificando respuesta: {e}")
            return {}
        
if __name__ == "__main__":
    obj = APIClient()
    encoded_text = "==QX9JycvlmchRXauVXbvNEI5ByclxWa05WYpRWd0NXRgM3b05WdzFEIlRGIh16wy9GdjVmcyV2YpZlI6ISZyJWbv5mIscTOyojIklmI7xSfiM3byJXYCByZyVmYlt2YuZ7wNBybk5WYuJXZGBicvR3YvREIy92clZ2byBFIsM3b05WZtlGbBBycvxGIlRGIh16wn9Gbv52YlRFI5BibzOcajlmc0VnTgUGZg8Gd1RXa0NnbJJiOiUmci12buJCLzADOxojIklmI7xSfiMXZsFmbvl2Yh5mclRnbJBycvlGZ1R3cFBSZkByb0VHdpR3culkI6ISZyJWbv5mIskDN4EjOiQWaisHL9JibzOcajF2Y1RWRg4WZgM3bkFmeuFmdBBycvlGZ1R3cFBSZkByb0VHdpR3culkI6ISZyJWbv5mIsUzN5EjOiQWaisHL9JycvNWasJmuDDFIz9GduV3cBBSZkByb0VHdpR3culkI6ISZyJWbv5mIskjM5EjOiQWaisHL9JybjlmbtOMbDBCbhRXawN3bIJiOiUmci12buJCL4UDMyojIklmI7xSfiEWrDf2bs9Gdu9GZPBSZkBCZhRHb1NWYGJiOiUmci12buJCLwYTNxojIklmI7xSfiEmbpNWakVWTgUGZgQWY0xWdjFmRiojIlJnYt9mbiwSM2ITM6ICZpJyes0nIv5mcllmYvdEIlRGIkFGdsV3YhZkI6ISZyJWbv5mIsIDO2IjOiQWaisHL9JyclRWYklmbh1WdIBSegEWrDb2bz9GbpZEIlRGIkFGdsV3YhZkI6ISZyJWbv5mIsITMyEjOiQWaisHL9Jycvl2YvdWZOBSegEWrD32bu92YFBSZkBCZhRHb1NWYGJiOiUmci12buJCL5QjN6ICZpJyes0nIvh2YlJXZEBSZkBCZhRHb1NWYGJiOiUmci12buJCL4ATMxojIklmI7xSfi4WZnFWbJBSZg42sDn2YhNWauVXbvNEIlRGIkFGdsV3YhZkI6ISZyJWbv5mIsMDO2IjOiQWaisHL9JychlmchV3YlBFI5Bychlmch5WayVGdlZFIzFWaj5WZpNEIlRGIkFGdsV3YhZkI6ISZyJWbv5mIsMjMwEjOiQWaisHL9JyclxWYpN2bTBychl2YuVWaDBSZkBCZhRHb1NWYGJiOiUmci12buJCLzQTO6ICZpJyes0nIzF2YpRXdpO8Yh1mchZEI5BychNWat16w1FFIzFWaj5WZpNEIlRGIkFGdsV3YhZkI6ISZyJWbv5mIsUTM5ojIklmI7xSfiMXYjlGdhOcblRXYNBSegMXYjl2ctOsRgMXYpNmbll2QgUGZgQWY0xWdjFmRiojIlJnYt9mbiwCO4cjOiQWaisHL9JielxWYyVHdh5EIhxGIlRGIuN7wpNWY2JXZz52bDBSYsBSZkBSegMXZsFGdzVmcvZEIzFWaj5WZpNEIlRGIkFGdsV3YhZkI6ISZyJWbv5mIsIDO4ojIklmI7xSfiMXYjlWbzOsbvJ3ZBBychl2YuVWaDBSZkBCZhRHb1NWYGJiOiUmci12buJCLwYTN6ICZpJyes0nIzFWaj5WZpNEIlRGIkFGdsV3YhZkI6ISZyJWbv5mIsYjM1ojIklmI7xSfiMXZ0JXQgUGZgQWY0xWdjFmRiojIlJnYt9mbiwCMyQjOiQWaisHL9JybtNXauFmYyVFI5BSYyVHdjVGdpVXcyFEIlRGIkFGdsV3YhZkI6ISZyJWbv5mIsgjMzojIklmI7xSfiICXuMEIuMFIuQkIcBCbhJXd0xWdDBSegE2YpR3ctOMdyFEIuN7wpNnblRHeFBSZkBybyRnblNkI6ISZyJWbv5mIsQjNyIjOiQWais3W"
    print(obj._decode_response(encoded_text=encoded_text))
