from bot import ScrunchScraper
from multiprocessing import Process


def proc_executor(i):
    scraper = ScrunchScraper(shift=i)
    scraper.run()


if __name__ == "__main__":
    procs = []
    for i in range(0, 30):
        proc = Process(target=proc_executor, args=(i,))
        procs.append(proc)
        proc.start()

    for proc in procs:
        proc.join()