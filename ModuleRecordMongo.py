import time
import recordMongo as rec


def main():
    while True:
        rec.RecordMongo.record_mongo()
        time.sleep(300)


if __name__ == '__main__':
    main()
