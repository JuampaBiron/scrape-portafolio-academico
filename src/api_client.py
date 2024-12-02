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
    encoded_text = "9NjOi8GZhRHb1NXZy9FbhR3b0JCL9NjOi8GZhRHb1NXZy9FbhR3b0JCLd1HM6IyclRWd0l2Ypx2bz9lbiwiIP5kI6ISYpNmblNWasJCLiIiOiQWY0xWdjFmZfFmclNmclRnIsIiI6ICZhRHb1NWYm9VYk5WdnV2ciwiIzF2YpRXoD3WZ0FWTgkHIzF2YpNXrDbEIzFWaj5WZpNEIlRGIkFGdsV3YhZkI6ICZhRHb1NWYmJCLi4WYpR3cpJ3Qg8GdyVmYtVHSiojIz92Yp1WZkF2YhJCLi42sDn2YuVmdulGIlRGIlRnblRXYQJiOiQWYkVWaw9mcw91boNWZyVGZiwiIz9mc09GIlJHduVGIsM3bjlWbhOsclNGIzVGbhlmclRXYtBCLzFmclNGIsMXZ0lWZjFGIsMXZsV2ZgwycvRnbllWbpR3clZXZyBCLzF2YhxGIsMXZjlmbyFmYgwychJXd05WawBCLz92Yp5WoDfmcvBycvRnbllWbpJnY1NWZyBCLzVGbiFGdzV2btJXZ0BybgMXYjlGdzF6wsB3btJXZ0BCLzF2YpRXqDTnbpNHIvByclxWYyVHdh5GIzF2YpJXqD3Was9GcgMXYul2clJHIv12bjByclxWY0BCLzVGbhlmclRXYtBycvRnbpR3cpRGIhBychRWaj9WaiBycvRWYkVWaw9mcwBSZyVWam52bjBSZ1FHIvZXa0lGZhJiOi8Gb1RXa0JCLiMTMwITLxATMyIiOiQWYklmcvlmcwJyes0HM6IyclRWd0l2Ypx2bz9lbiwiIP5kI6ISYpNmblNWasJCLiIiOiQWY0xWdjFmZfFmclNmclRnIsIiI6ICZhRHb1NWYm9VYk5WdnV2ciwiIzF2YpRXoD3WZ0FWTgkHIzF2YpNXrDbEIzFWaj5WZpNEIlRGIkFGdsV3YhZkI6ICZhRHb1NWYmJCLi4WYpR3cpJ3Qg8GdyVmYtVHSiojIz92Yp1WZkF2YhJCLi42sDn2YuVmdulGIlRGIlRnblRXYQJiOiQWYkVWaw9mcw91boNWZyVGZiwiIz92c1Byc1NHI5Bibvl2YhJ3biFGblBSZkBybk9Gdl1GIsMXYuFWai9mcjlWbpRnbhBSegMXZsFmcpZXa05WYgwychRWaj9WaiBCLn5WasV3bnlGduFGIzVGZhRWZpB3byBHIu92YgM3bjlmcl1Was9GcgMXZsFWayVGdh1mI6IybsVHdpRnIsIiMxAjMtATNzIjI6ICZhRWay9WayBnI7xSfwojIzVGZ1RXajlGbvN3XuJCLi8kTiojIhl2YuV2YpxmIsIiI6ICZhRHb1NWYm9VYyV2YyVGdiwiIiojIkFGdsV3YhZ2XhRmb1dWZzJCLiMXYjlGdhOcblRXYNBSegMXYjl2ctOsRgMXYpNmbll2QgUGZgQWY0xWdjFmRiojIkFGdsV3YhZmIsIibhlGdzlmcDByb0JXZi1WdIJiOiM3bjlWblRWYjFmIsIibzOcaj5WZ25WagUGZgUGduVGdhBlI6ICZhRWZpB3byB3Xvh2YlJXZkJCLiM3bzVHIzV3cgkHIuN7wpNWYy9mYhxWZgUGZg8GZvRXqD3GIuMXYuFWai9mcjlWbpRnbhBSegMXZsFmcpZXa05WYgwychRWaj9WaiBCLn5WasV3bmlGduFGIzVGZhRWZpB3byBHIu92YgM3bjlmcpOcbpx2bwByclxWYpJXZ0FWbiojIvxWd0lGdiwiIxEDMy0yM1gjMiojIkFGZpJ3bpJHcis3W6IyclRnblRXYwJCL0IDMxMjOiEmbvNnclB3XklmI7pjIz92Yp1WZkF2YhJye"
    print(obj._decode_response(encoded_text=encoded_text))
