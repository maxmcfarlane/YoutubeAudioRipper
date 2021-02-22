from youtuberipper.rip import rip_URLs, rip_AUDIO

if __name__ == '__main__':
    df_urls = rip_URLs()
    rip_AUDIO(df_urls)
