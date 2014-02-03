from src.KongAPI import *

def main():
        myUser = KongAuthUser('resterman')
        myUser.login('pass')

if __name__ == '__main__':
        main()
