#!/usr/bin/env python
# coding: UTF-8

import time
def start_log_to_file(source,etape,dept):
        t = time.localtime()
        th =  time.strftime('%d-%m-%Y %H:%M:%S',t)
        t = round(time.mktime(t),0)
	log_filename = '{:s}_{:s}_{:s}.log'.format(dept,etape,source)
	f = open('./logs/{:s}'.format(log_filename),'w+')
	f.write('Debut : {:s}\n'.format(th))
	f.flush()
	return f

def write_log_to_file(flog,message):
	flog.write(message+'\n')
	flog.flush()

def write_sep_to_file(flog):
        flog.write('\n####################\n')
        flog.flush()

def end_log_to_file(flog,display):
        t = time.localtime()
        th =  time.strftime('%d-%m-%Y %H:%M:%S',t)
        flog.write(u'Fin   : {:s}\n'.format(th))
        flog.flush()
	if display:
		flog.seek(0)
		print(flog.read())
	flog.close()

