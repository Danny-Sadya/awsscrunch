from bot2 import ScrunchScraper
from multiprocessing import Process


def proc_executor(args):
    scraper = ScrunchScraper(dargs=args)
    scraper.run()


if __name__ == "__main__":
    parametres = {
        "engagement_rate": ['0.01%2C0.02', '0.02%2C0.03', '0.03%2C0.04', '0.04%2C0.05', '0.05%2C0.06', '0.06%2C0.07,'
                                                                '0.07%2C0.08', '0.09%2C0.1'],
        "location": ['6255146', '6255147', '6255148', '6255149', '6255150', '6255151', '6255152'],
        "topic": ['adult', 'animals%20%26%20pets', 'anime%20%26%20manga', 'architecture', 'automotive', 'beauty',
                  'boating', 'books', 'business%20%26%20finance', 'celebrity%20gossip', 'cosplay', 'design',
                  'education', 'environment', 'family', 'fashion', 'food%20%26%20drink', 'gaming', 'garden',
                  'graphic%20novels%20%26%20comics', 'health%20%26%20fitness', 'home%20interior', 'medicine',
                  'music', 'news%20%26%20media', 'not%20for%20profit', 'photography', 'politics', 'relationships',
                  'sciences', 'self%20help%20%26%20well%20being', 'sexuality', 'smoking%20%26%20vaping', 'spiritual',
                  'sport', 'tattoos', 'technology', 'the%20arts', 'travel', 'tv%20%26%20film', 'wedding'],
        "age": ['18-24', '25-34', '35-44', '45-54', '55-64', '65%2B'],
        "gender": ['m', 'f']
    }
    procs = []
    # t1 = {'engagement_rate': parametres['engagement_rate'][0],
    #       'topic': ['fashion', 'travel', 'music', 'beauty'],
    #       'gender': parametres['gender']}

    for i in range(0, 1):
        topics = ['fashion', 'travel', 'music', 'beauty', 'relationships', 'travel', 'sport', 'design', 'sciences', 'cosplay']
        proc = Process(target=proc_executor, args=({'engagement_rate': parametres['engagement_rate'],
                                                      'topic': topics[i],
                                                      'gender': parametres['gender'],
                                                    'shift': i},))
        procs.append(proc)
        proc.start()

    for proc in procs:
        proc.join()

