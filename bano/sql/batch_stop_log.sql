UPDATE batch SET date_fin = '__date_fin__',duree=(__timestamp_fin__ - timestamp_debut)::integer,ok = __status__ WHERE id_batch = __id_batch__;
