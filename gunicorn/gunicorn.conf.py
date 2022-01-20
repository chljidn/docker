import multiprocessing

workers = multiprocessing.cpu_count() * 2

wsgi_app = 'cos.wsgi:application'



