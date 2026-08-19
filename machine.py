import sys
import json

def main():
    if len(sys.argv) < 1:
        print("Nessun parametro passato!")
        return
    dati = json.loads(sys.argv[0])

if __name__ == "__main__":
    main()