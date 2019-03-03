mkdir -p results
cd results
curl http://prezydent2000.pkw.gov.pl/gminy/obwody/obw\[01-68\].xls -o "obw#1.xls"
curl http://prezydent2000.pkw.gov.pl/gminy/zal1.xls -o "zal1.xls"
curl http://prezydent2000.pkw.gov.pl/gminy/zal2.xls -o "zal2.xls"
cd ..

python3 -m venv ../gen
source ../gen/bin/activate

pip install django
pip install jinja2
pip install numpy
pip install xlrd xlwt
python3 generate.py