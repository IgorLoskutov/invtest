import hashlib

from app import app



def sign(data: dict):
	sorted_keys = sorted(data.keys())
	
	hash_string = ':'.join([str(data[key]) for key in sorted_keys]) + app.config['SHOP_SECRET_KEY']
	print(hash_string)
	hash = hashlib.sha256(bytes(hash_string, 'utf-8'))
	return hash.hexdigest()