from pyape.util.gen import gen_secret_key

def test_gen_secret_key():
    secret_key =  gen_secret_key()
    print(secret_key)