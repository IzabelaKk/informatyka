# -*- coding: utf-8 -*-
"""
Created on Fri Apr 28 00:53:31 2023

@author: Dell
"""

from math import *
import numpy as np
import argparse


class transformacje():
    
    def __init__(self, model: str):
        """
        
        Parametry elipsolidy:
        ----------
        a - duża półoś elispoidy
        b - mała półoś elipsoidy
        flat - spłaszczenie
        e - mimośród
        e2 - mimośród podniesiony do kwadratu

        """
        if model == "wgs84":
            self.a = 6378137
            self.b = 6356752.31424518 
        elif model == "grs80":
            self.a = 6378137
            self.b = 6356752.31414036
        elif model == "krasowski":
            self.a = 6378245
            self.b = 6356863.019  #jakby był potrzebny mimosrod i f http://uriasz.am.szczecin.pl/naw_bezp/elipsoida.html
        else:
            raise NotImplementedError(f"{model} nie został zaimplementowany")
        self.flat = (self.a - self.b) / self.a
        self.e = sqrt(2 * self.flat - self.flat ** 2) 
        self.e2 = (2 * self.flat - self.flat ** 2)
        

            
    def dms(self, txt, x):
        """
        Funkcja przeliczająca wartość wyrażoną w radianach na wartość wyrażoną w stopniach, minutach i sekundach
        ----------
        x : FLOAT
        wartość w radianach
        
        Zwraca:
        -------
        dms - stopnie, minuty, sekundy
        """
 
        sig = ' '
        if x < 0:
            sig = '-'
            x = abs(x)
        x = x * 180/pi
        d = int(x)
        m = int(60 * (x - d))
        s = (x - d - m/60)*3600

        print(txt,sig,'%3d' % d,'°', '%2d' % m,"'",'%7.5f' % s,'"')

        return f"{txt} {sig} {d:3d}° {m:2d}' {s:7.5f}\""

        
        
        
    def Np(self,f):
        """
        Funkcja okreslająca przekrój poprzeczny w I wertykale
        -------
        a - duża półoś elispoidy
        f - spłaszczenie
        e2 - mimośród podniesiony do kwadratu
        
        Zwraca:
        -------
        Wartosć przekroju poprzecznego w I wetykale

        """
        N = self.a / np.sqrt(1 - self.e2 * np.sin(f)**2)
        return(N)
    
    
    def Mp(self):
        """
        Funkcja wyznaczająca promień przekroju normalnego w kierunku głównym
        -------
        a - duża półoś elispoidy
        f - spłaszczenie
        e2 - mimośród podniesiony do kwadratu
        
        Zwraca:
        -------
        Wartosc promienia przekroju przekroju normalnego w kierunku głównym. 
        """
        M = self.a * (1 - self.e2) / np.sqrt((1 - self.e2 * np.sin(flat)**2)**3)
        return(M)
            
            
    def XYZ2flh(self, X, Y, Z):
        """
        Algorytm Hirvonena - algorytm transformacji współrzędnych ortokartezjańskich (x, y, z)
        na współrzędne geodezyjne długość szerokość i wysokośc elipsoidalna (phi, lam, h). Jest to proces iteracyjny. 
        W wyniku 3-4-krotneej iteracji wyznaczenia wsp. phi można przeliczyć współrzędne z dokładnoscią ok 1 cm.     
        Parametry:
        ----------
        X, Y, Z : FLOAT
             współrzędne w układzie orto-kartezjańskim, 

        Zwraca:
        -------
        phi - szerokość geodezyjna w stopniach dziesiętnych
        lam - długośc geodezyjna w stopniach dziesiętnych
        h - wysokość elipsoidalna w metrach
        """
        p = np.sqrt(X**2 + Y**2)
        f = np.arctan(Z/(p*(1-self.e2)))
        while True:
            N = self.Np(f)
            fpop = f
            h = (p/np.cos(f))-N
            fl = np.arctan(Z/(p*(1-self.e2*N/(N+h))))
            if abs(fpop-f) < (0.000001/206265):
                break
        l = np.arctan2(Y,X)
        return(degrees(f), degrees(l), h)
    

    
    def flh2XYZ(self, f, l, h):
        """
        Funkcja przeliczająca współrzędne geodezyjne (phi, lam h) na współrzędne ortokartezjańskie (X, Y, Z)

        Parametry:
        ----------
        f : FLOAT
            szerokosć geodezyjna wyrażona w radianach ?????????????????
        l : FLOAT
            długosć geodezyjna wyrażona w radianach
        h : FLOAT
            wysokosć elipsoidalna wyrażona w metrach

        Returns
        -------
        X - [metry]
        Y - [metry]
        Z - [metry]

        """
        N = self.Np(f)
        X = (N + h) * cos(f) * cos(l)
        Y = (N + h) * cos(f) * sin(l)
        Z = (N * (1 - self.e2) + h) * sin(f)
        return(X,Y,Z)
    
    def u1992(self, f, l):
        """
        
        Odwzorowanie Gausa Krugera do układu 1992. Odnosi się do południka osiowego 19 stopni. 
        Współrzędne wejsciowe zostają odwzorowane na do układu lokalnego GK a następnie przeskalowane zgodnie z układem 1992.
        Parametry:
        ---------
        f:  FLOAT
        szerokoć geodezyjna wyrażona w radianach
        l:  FLOAT
        długoć geodezyjna wyrażona w radianach
        Returns:
        ---------
        x:  FLOAT
        szerokosc prostkątna lokalna wyrażona w metrach
        y:  FLOAT
        długosc prostokątna lokalna wyrażona w metrach

        """
        m = 0.9993
        N = self.Np(f)
        t = np.tan(f)
        e_2 = self.e2/(1-self.e2)
        n2 = e_2 * (np.cos(f))**2

        l0 = 19 * np.pi / 180
        d_l = l - l0
            
        A0 = 1 - (self.e2/4) - ((3*(self.e2**2))/64) - ((5*(self.e2**3))/256)   
        A2 = (3/8) * (self.e2 + ((self.e2**2)/4) + ((15 * (self.e2**3))/128))
        A4 = (15/256) * (self.e2**2 + ((3*(self.e2**3))/4))
        A6 = (35 * (self.e2**3))/3072 
    
        sigma = self.a * ((A0*f) - (A2*np.sin(2*f)) + (A4*np.sin(4*f)) - (A6*np.sin(6*f)))
    
        xgk = sigma + ((d_l**2)/2) * N *np.sin(f) * np.cos(f) * (1 + ((d_l**2)/12) * ((np.cos(f))**2) * (5 - t**2 + 9*n2 + 4*(n2**2)) + ((d_l**4)/360) * ((np.cos(f))**4) * (61 - (58*(t**2)) + (t**4) + (270*n2) - (330 * n2 *(t**2))))
        ygk = d_l * (N*np.cos(f)) * (1 + ((((d_l**2)/6) * (np.cos(f))**2) * (1-t**2+n2)) +  (((d_l**4)/(120)) * (np.cos(f)**4)) * (5 - (18 * (t**2)) + (t**4) + (14*n2) - (58*n2*(t**2))))
    
        x92 = m*xgk - 5300000
        y92 = m*ygk + 500000
        
        return (x92, y92)
        
    
    
    def u2000(self, f, l):
        """
        Odwzorowanie odnosi się do odwzorowania GK bazującego tym razem na czterech południkach osiowych:
        15, 18, 21, 24. Funkcja odwzorowuje współrzędne wejsciowe na współrzędne prostokątne lokalne GK
        a następnie przeskalowuje je zgodnie zparametrami układu 2000.

        Parametry:
        ---------
        f:  FLOAT
            szerokoć geodezyjna wyrażona w radianach
        l:  FLOAT
            długoć geodezyjna wyrażona w radianach
        Returns:
        ---------
        x:  FLOAT
            szerokosc prostkątna lokalna wyrażona w metrach
        y:  FLOAT
            długosc prostokątna lokalna wyrażona w metrach

        """
        m = 0.999923
        N=self.Np(f)
        t = np.tan(f)
        e_2 = self.e2/(1-self.e2)
        n2 = e_2 * (np.cos(f))**2
        
        l = l * 180 / np.pi
        if l>13.5 and l <16.5:
            s = 5
            l0 = 15
        elif l>16.5 and l <19.5:
            s = 6
            l0 = 18
        elif l>19.5 and l <22.5:
            s = 7
            l0 = 21
        elif l>22.5 and l <25.5:
            s = 8
            l0 = 24
            
        l = l* np.pi / 180
        l0 = l0 * np.pi / 180
        d_l = l - l0

        A0 = 1 - (self.e2/4) - ((3*(self.e2**2))/64) - ((5*(self.e2**3))/256)   
        A2 = (3/8) * (self.e2 + ((self.e2**2)/4) + ((15 * (self.e2**3))/128))
        A4 = (15/256) * (self.e2**2 + ((3*(self.e2**3))/4))
        A6 = (35 * (self.e2**3))/3072 
        

        sig = self.a * ((A0*f) - (A2*np.sin(2*f)) + (A4*np.sin(4*f)) - (A6*np.sin(6*f)))
        
        xgk = sig + ((d_l**2)/2) * N *np.sin(f) * np.cos(f) * (1 + ((d_l**2)/12) * ((np.cos(f))**2) * (5 - t**2 + 9*n2 + 4*(n2**2)) + ((d_l**4)/360) * ((np.cos(f))**4) * (61 - (58*(t**2)) + (t**4) + (270*n2) - (330 * n2 *(t**2))))
        ygk = d_l * (N*np.cos(f)) * (1 + ((((d_l**2)/6) * (np.cos(f))**2) * (1-t**2+n2)) +  (((d_l**4)/(120)) * (np.cos(f)**4)) * (5 - (18 * (t**2)) + (t**4) + (14*n2) - (58*n2*(t**2))))
        
        x00 =m * xgk
        y00 =m * ygk + (s*1000000) + 500000
         
        return(x00, y00)
    
    
    def XYZ2neu(self, dXYZ, f, l, s, alfa, z):
        p = np.sqrt(X**2 + Y**2)
        f = np.arctan(Z/(p*(1-self.e2)))
        while True:
            N = self.Np(f)
            fpop = f
            h = (p/np.cos(f))-N
            fl = np.arctan(Z/(p*(1-self.e2*N/(N+h))))
            if abs(fpop-f) < (0.000001/206265):
                break
        l = np.arctan2(Y,X)
        
        R = np.array([[-np.sin(f) * np.cos(l), -np.sin(l), np.cos(f) * cos(l)],
                      [-np.sin(f) * np.sin(l), np.cos(l), np.cos(f) * np.sin(l)],
                      [np.cos(f), 0, np.sin(f)]])
        
        dneu = np.array([s * np.sin(z) * np.cos(alfa),
                         s * np.sin(z) * np.sin(alfa),
                         s * cos(z)])
        return(dneu[0], dneu[1], dneu[2])
    

if __name__ == "__main__":
    geo = transformacje(model = "wgs84")
    X = 3853110.000; Y = 1425020.000; Z = 4863030.000
    phi, lam, h = geo.XYZ2flh(X, Y, Z)
    print('f: ', round(phi,5), 'l: ', round(lam,5), 'h: ', round(h, 3))
    
if __name__ == "__main__":
    geo = transformacje(model = "wgs84")
    f = 0.8726510197633319; l = 0.3542359357681509; h = 387.3190605593845
    X, Y, Z = geo.flh2XYZ(f, l, h)
    print('X: ', round(X,3), 'Y: ', round(Y,3), 'Z: ', round(Z, 3))

if __name__ == "__main__":
    geo = transformacje(model = "wgs84")
    f = 0.8726510197633319; l = 0.3542359357681509; h = 387.3190605593845
    x92, y92 = geo.u1992(f, l)
    print('x92: ', round(x92, 3), 'y92: ', round(y92,3))

if __name__ == "__main__":
    geo = transformacje(model = "wgs84")
    f = 0.8726510197633319; l = 0.3542359357681509; h = 387.3190605593845
    x00, y00 = geo.u2000(f, l)
    print('x00: ', round(x00, 3), 'y00: ', round(y00,3))
    
"""if __name__ == "__main__":
    geo = transformacje(model = "wgs84")
    X = 0.8726510197633319; Y = 0.3542359357681509; Z = 387.3190605593845
    n, e, u = geo.XYZ2neu(dXYZ, f, l, s, alfa, z)
    print(n, e, u)"""
 
 #tu cos nie gra chyba trzeba zrobic ta inna wersje
"""
if __name__ == "__main__":
    
    trans = transformacje(self.model)
    pars = argparse.ArgumentParser(description = "Transformacje współrzędnych")
    pars.add_argument(dest = "Metoda", metavar = 'M', nargs = 1, type = str,
                      help = 'napisz nazwe metody (wymienic metody)')
    pars.add_argument(dest = 'Załączanie danych', metavar = 'L', nargs = 1, type = str,
                      help = 'jak chcesz wprowadzac tane txt, input')
        
    pars.add_argument(dest = 'dane', metavar = 'D', type = float, nargs = '+',
                      help = 'wsp do zamiany')
    
    args = pars.parse_args()
    print(args)
    """
"""
if __name__ == "__main__":
    
    parser = ArgumentParser()
  
    parser.add_argument('-d', type = str, help = 'Plik nie znajduje się w odpowiednim folderze. Podaj scieżkę do pliku.')
    parser.add_argument('-t', type = str, help = 'Wybrana transformacja (XYZ2flh, flh2XYZ, u1992, u2000, XYZ2neu)')
    parser.add_argument('-e', type = str, help = 'Przyjmuje model elipsoidy (WGS84, GRS80, krasowski)')
    
    args = parser.parse_args()
#funkcja = getattr(trans, args.method[0])
     
#with open(wyniki.txt, 'w') as plik:
"""