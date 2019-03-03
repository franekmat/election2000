""" - """
from collections import defaultdict
from shutil import copyfile
from distutils.dir_util import copy_tree
import os
import xlrd
import consts
from jinja2 import Environment, FileSystemLoader

def main():
    """ - """
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)
    dane_ = xlrd.open_workbook('results/zal1.xls')
    dane = dane_.sheet_by_name('Zal1')
    dane2_ = xlrd.open_workbook('results/zal2.xls')
    dane2 = dane2_.sheet_by_name('Zal2')
    okregi = []
    gminy = defaultdict(list)
    nazwagminy = defaultdict(list)
    obwody = defaultdict(list)
    nazwaobwodu = defaultdict(list)
    kodobwodu = defaultdict(list)
    miasta = defaultdict(list)
    nazwamiasta = defaultdict(list)
    wyniki = {}
    glosy = defaultdict(lambda: 0, {})
    uprawnieni = defaultdict(lambda: 0, {})
    wydane = defaultdict(lambda: 0, {})
    oddane = defaultdict(lambda: 0, {})
    wazne = defaultdict(lambda: 0, {})
    niewazne = defaultdict(lambda: 0, {})

    def formatuj(liczba):
        return format(int(round(liczba)), ',').replace(',', ' ')

    def generuj_kraj(szablon):
        template = env.get_template(szablon)
        if not os.path.isdir('page'):
            os.mkdir('page')
        copyfile("templates/style.css", "page/style.css")
        os.chdir('page')
        results = []
        kandydaci = []
        k = 3
        for kand in consts.KANDYDACI:
            kandydat = dict(nazwisko=kand,
                            glosy=formatuj(dane2.cell(6, k).value),
                            wynik=round(dane2.cell(6, k + 1).value * 100, 2))
            results.append(dane2.cell(6, k).value)
            kandydaci.append(kandydat)
            k += 2

        uprawnieni = dane.cell(5, 3).value
        wydane = dane.cell(5, 4).value
        oddane = dane.cell(5, 6).value
        wazne = dane.cell(5, 7).value
        niewazne = dane.cell(5, 9).value
        frekwencja = dane.cell(5, 5).value

        paths = [('', 'Polska')]

        template.stream(
            uprawnieni=formatuj((uprawnieni)),
            wydane=formatuj(wydane),
            oddane=formatuj(oddane),
            wazne=formatuj(wazne),
            niewazne=formatuj(niewazne),
            frekwencja=str(round(frekwencja * 100, 2))+'%',
            kandydaci=kandydaci,
            mapa=True,
            nazwa_linki='Mapa',
            bootstrapstyle='bootstrap/css/bootstrap.min.css',
            bootstrapjs='bootstrap/js/bootstrap.min.js',
            style='style.css',
            paths=paths,
            res=results
            ).dump('index.html')
        os.chdir("../")

    def generuj_wojewodztwa(szablon):
        template = env.get_template(szablon)
        os.chdir('page')
        for woj in consts.WOJEWODZTWA:
            if not os.path.isdir(woj):
                os.mkdir(woj)
            for j in range(6, dane.nrows):
                if woj == dane.cell(j, 1).value.lower():
                    j += 1
                    while j < dane.nrows and dane.cell(j, 0).value != 'województwo':
                        kod_miasta = int(round(dane.cell(j, 0).value))
                        miasta[woj].append(kod_miasta)
                        nazwamiasta[kod_miasta] = dane.cell(j, 1).value
                        uprawnieni[woj] += dane.cell(j, 3).value
                        uprawnieni[kod_miasta] += dane.cell(j, 3).value
                        wydane[woj] += dane.cell(j, 4).value
                        wydane[kod_miasta] += dane.cell(j, 4).value
                        oddane[woj] += dane.cell(j, 6).value
                        oddane[kod_miasta] += dane.cell(j, 6).value
                        wazne[woj] += dane.cell(j, 7).value
                        wazne[kod_miasta] += dane.cell(j, 7).value
                        niewazne[woj] += dane.cell(j, 9).value
                        niewazne[kod_miasta] += dane.cell(j, 9).value
                        j += 1
                    break
            for j in range(7, dane2.nrows):
                if woj == dane2.cell(j, 1).value.lower():
                    j += 1
                    while j < dane2.nrows and dane2.cell(j, 0).value != 'województwo':
                        k = 3
                        kod_miasta = int(round(dane2.cell(j, 0).value))
                        for kand in consts.KANDYDACI:
                            glosy[kand + woj] += dane2.cell(j, k).value
                            glosy[kand + str(kod_miasta)] = dane2.cell(j, k).value
                            wyniki[kand + str(kod_miasta)] = dane2.cell(j, k + 1).value
                            k += 2
                        j += 1
                    break
            kandydaci = []
            results = []
            for kand in consts.KANDYDACI:
                kandydat = dict(nazwisko=kand,
                                glosy=formatuj(glosy[kand + woj]),
                                wynik=round(glosy[kand + woj] / oddane[woj] * 100, 2))
                results.append(glosy[kand + woj])
                kandydaci.append(kandydat)
            lista_miast = []
            for miasto in miasta[woj]:
                lista_miast.append('<a href="' + str(miasto).replace(" ", "") +
                                   '/index.html" class="list-group-item list-group-item-action">' +
                                   nazwamiasta[miasto] +
                                   ' (okręg nr ' + str(miasto) + ')</a>')
            paths = [('../index.html', 'Polska'),
                     ('../' + woj + '/index.html', woj)]
            template.stream(
                uprawnieni=formatuj(uprawnieni[woj]),
                wydane=formatuj(wydane[woj]),
                oddane=formatuj(oddane[woj]),
                wazne=formatuj(wazne[woj]),
                niewazne=formatuj(niewazne[woj]),
                frekwencja=str(round(oddane[woj] / uprawnieni[woj] * 100, 2)) + '%',
                kandydaci=kandydaci,
                linki=lista_miast,
                nazwa_linki='Okręgi',
                bootstrapstyle='../bootstrap/css/bootstrap.min.css',
                bootstrapjs='../bootstrap/js/bootstrap.min.js',
                style='../style.css',
                paths=paths,
                res=results
            ).dump(woj + '/index.html')
        os.chdir("../")

    def czytaj_okregi():
        okregi_tmp = []
        okregi_tmp.append(0)
        okregi.append(0)
        for i in range(1, consts.LICZBA_OKREGOW + 1):
            okregi_tmp.append(i)
            okregi_tmp[i] = xlrd.open_workbook('results/obw%02d.xls' % i)
            okregi.append(i)
            okregi[i] = okregi_tmp[i].sheet_by_index(0)

    def generuj_okregi(szablon):
        template = env.get_template(szablon)
        os.chdir('page')
        for woj in consts.WOJEWODZTWA:
            os.chdir(woj)
            for miasto in miasta[woj]:
                if not os.path.isdir(str(miasto)):
                    os.mkdir(str(miasto))
                for i in range(1, okregi[miasto].nrows):
                    gmina = okregi[miasto].cell(i, 1).value
                    if okregi[miasto].cell(i, 2).value != okregi[miasto].cell(i - 1, 2).value:
                        gminy[miasto].append(gmina)
                        nazwagminy[gmina] = okregi[miasto].cell(i, 2).value
                    obwod = str(gmina) + str(okregi[miasto].cell(i, 4).value)
                    obwody[gmina].append(obwod)
                    nazwaobwodu[obwod] = okregi[miasto].cell(i, 6).value
                    kodobwodu[obwod] = int(round(okregi[miasto].cell(i, 4).value))
                    uprawnieni[gmina] += okregi[miasto].cell(i, 7).value
                    uprawnieni[obwod] = okregi[miasto].cell(i, 7).value
                    wydane[gmina] += okregi[miasto].cell(i, 8).value
                    wydane[obwod] = okregi[miasto].cell(i, 8).value
                    oddane[gmina] += okregi[miasto].cell(i, 9).value
                    oddane[obwod] = okregi[miasto].cell(i, 9).value
                    wazne[gmina] += okregi[miasto].cell(i, 11).value
                    wazne[obwod] = okregi[miasto].cell(i, 11).value
                    niewazne[gmina] += okregi[miasto].cell(i, 10).value
                    niewazne[obwod] = okregi[miasto].cell(i, 10).value
                    k = 12
                    for kand in consts.KANDYDACI:
                        glosy[kand + obwod] = okregi[miasto].cell(i, k).value
                        glosy[kand + str(gmina)] += okregi[miasto].cell(i, k).value
                        k += 1
                lista_gmin = []
                for gmina in gminy[miasto]:
                    lista_gmin.append('<a href="' + str(gmina).replace(" ", "") +
                                      '/index.html" class="list-group-item '
                                      'list-group-item-action">' +
                                      nazwagminy[gmina] + '</a>')
                kandydaci = []
                results = []
                for kand in consts.KANDYDACI:
                    kandydat = dict(nazwisko=kand,
                                    glosy=formatuj(glosy[kand + str(miasto)]),
                                    wynik=round(glosy[kand + str(miasto)] /
                                                oddane[miasto] * 100, 2))
                    results.append(glosy[kand + str(miasto)])
                    kandydaci.append(kandydat)
                paths = [('../../index.html', 'Polska'),
                         ('../index.html', woj),
                         ('../' + str(miasto) + '/index.html',
                          nazwamiasta[miasto] + ' (okręg nr ' + str(miasto) + ')')]
                template.stream(
                    uprawnieni=formatuj(uprawnieni[miasto]),
                    wydane=formatuj(wydane[miasto]),
                    oddane=formatuj(oddane[miasto]),
                    wazne=formatuj(wazne[miasto]),
                    niewazne=formatuj(niewazne[miasto]),
                    frekwencja=str(round(oddane[miasto] / uprawnieni[miasto] * 100, 2)) + '%',
                    kandydaci=kandydaci,
                    linki=lista_gmin,
                    nazwa_linki='Gminy',
                    bootstrapstyle='../../bootstrap/css/bootstrap.min.css',
                    bootstrapjs='../../bootstrap/js/bootstrap.min.js',
                    style='../../style.css',
                    paths=paths,
                    res=results
                ).dump(str(miasto) + '/index.html')
            os.chdir("../")
        os.chdir("../")

    def generuj_gminy(szablon):
        template = env.get_template(szablon)
        os.chdir('page')
        for woj in consts.WOJEWODZTWA:
            os.chdir(woj)
            for miasto in miasta[woj]:
                os.chdir(str(miasto))
                for gmina in gminy[miasto]:
                    if not os.path.isdir(str(gmina)):
                        os.mkdir(str(gmina))
                    lista_obwodow = []
                    for obwod in obwody[gmina]:
                        lista_obwodow.append('<a href="' +
                                             str(kodobwodu[obwod]).replace(" ", "") +
                                             '/index.html" class="list-group-item '
                                             'list-group-item-action">' +
                                             'Obwód nr ' + str(kodobwodu[obwod]) + '</a>')
                    kandydaci = []
                    results = []
                    for kand in consts.KANDYDACI:
                        kandydat = dict(nazwisko=kand,
                                        glosy=formatuj(glosy[kand + str(gmina)]),
                                        wynik=round(glosy[kand + str(gmina)] /
                                                    oddane[gmina] * 100, 2))
                        results.append(glosy[kand + str(gmina)])
                        kandydaci.append(kandydat)
                    paths = [('../../../index.html', 'Polska'),
                             ('../../index.html', woj),
                             ('../index.html', nazwamiasta[miasto] +
                              ' (okręg nr ' + str(miasto) + ')'),
                             ('../' + str(gmina) + '/index.html', nazwagminy[gmina])]
                    template.stream(
                        uprawnieni=formatuj(uprawnieni[gmina]),
                        wydane=formatuj(wydane[gmina]),
                        oddane=formatuj(oddane[gmina]),
                        wazne=formatuj(wazne[gmina]),
                        niewazne=formatuj(niewazne[gmina]),
                        frekwencja=str(round(oddane[gmina] / uprawnieni[gmina] * 100, 2)) + '%',
                        kandydaci=kandydaci,
                        nazwa_linki='Obwody',
                        linki=lista_obwodow,
                        bootstrapstyle='../../../bootstrap/css/bootstrap.min.css',
                        bootstrapjs='../../../bootstrap/js/bootstrap.min.js',
                        style='../../../style.css',
                        paths=paths,
                        res=results
                    ).dump(str(gmina) + '/index.html')
                os.chdir("../")
            os.chdir("../")
        os.chdir("../")

    def generuj_obwody(szablon):
        template = env.get_template(szablon)
        os.chdir('page')
        for woj in consts.WOJEWODZTWA:
            os.chdir(woj)
            for miasto in miasta[woj]:
                os.chdir(str(miasto))
                for gmina in gminy[miasto]:
                    os.chdir(str(gmina))
                    for obwod in obwody[gmina]:
                        if not os.path.isdir(str(kodobwodu[obwod])):
                            os.mkdir(str(kodobwodu[obwod]))
                        kandydaci = []
                        results = []
                        if oddane[obwod] > 0:
                            for kand in consts.KANDYDACI:
                                kandydat = dict(nazwisko=kand,
                                                glosy=formatuj(glosy[kand + obwod]),
                                                wynik=round(glosy[kand + obwod] /
                                                            oddane[obwod] * 100, 2))
                                results.append(glosy[kand + obwod])
                                kandydaci.append(kandydat)
                        else:
                            for kand in consts.KANDYDACI:
                                kandydat = dict(nazwisko=kand,
                                                glosy=formatuj(glosy[kand + obwod]),
                                                wynik=0)
                                results.append(glosy[kand + obwod])
                                kandydaci.append(kandydat)
                        paths = [('../../../../index.html', 'Polska'),
                                 ('../../../index.html', woj),
                                 ('../../index.html', nazwamiasta[miasto] +
                                  ' (okręg nr ' + str(miasto) + ')'),
                                 ('../index.html', nazwagminy[gmina]),
                                 ('../' + str(kodobwodu[obwod]) + '/index.html',
                                  'Obwód nr ' + str(kodobwodu[obwod]))]
                        template.stream(
                            uprawnieni=formatuj(uprawnieni[obwod]),
                            wydane=formatuj(wydane[obwod]),
                            oddane=formatuj(oddane[obwod]),
                            wazne=formatuj(wazne[obwod]),
                            niewazne=formatuj(niewazne[obwod]),
                            frekwencja=str(round(oddane[obwod] / uprawnieni[obwod] * 100, 2)) + '%',
                            kandydaci=kandydaci,
                            bootstrapstyle='../../../../bootstrap/css/bootstrap.min.css',
                            bootstrapjs='../../../../bootstrap/js/bootstrap.min.js',
                            style='../../../../style.css',
                            paths=paths,
                            res=results
                        ).dump(str(kodobwodu[obwod]) + '/index.html')
                    os.chdir("../")
                os.chdir("../")
            os.chdir("../")
        os.chdir("../")

    copy_tree('bootstrap', 'page/bootstrap')
    print("Generuję kraj....")
    generuj_kraj('main.html')
    print("Generuję województwa....")
    generuj_wojewodztwa('main.html')
    czytaj_okregi()
    print("Generuję okręgi.....")
    generuj_okregi('main.html')
    print("Generuję gminy....")
    generuj_gminy('main.html')
    print("Generuję obwody....")
    generuj_obwody('main.html')

main()
