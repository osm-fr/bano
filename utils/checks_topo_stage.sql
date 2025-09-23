select 'topo stage',max(date_creation) from topo_stage
union all
select 'topo ',max(date_creation) from topo;

select test,count(*) from topo_comparaison
group by 1;

with
t
as
(select substr(code,1,5) as com,count(*)
from topo_comparaison
group by 1),
f
as
(select dep,libelle,count,com
from cog_commune join t
using (com)
--where comparent is null
where typecom = 'COM'
order by 3 desc)
select '|'||dep||'|'||libelle||'|'||count||'|https://bano.openstreetmap.fr/pifometre/index.html?insee='||com||'|'
from f
limit 10;
