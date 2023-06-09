import numpy as np
from math import degrees
from argparse import ArgumentParser


class transformacje():
    
    def __init__(self, model: str = "wgs84"):
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
            self.b = 6356863.019  
        else:
            raise NotImplementedError(f"{model} nie został zaimplementowany")

        self.flat = (self.a - self.b) / self.a
        self.e = np.sqrt(2 * self.flat - self.flat ** 2) 
        self.e2 = (2 * self.flat - self.flat ** 2)
        

            
    
    
    def danezpl(self, txt):
        with open(txt, 'r') as plik:
            linie = plik.readlines()
            dane = []
            for i in linie:
                i = i.replace(',', ' ').split()
                dane.append([float(j) for j in i])
        return dane
            
    
    def wyniki(self, plik, wyniki):
        with open(plik, 'w') as plik:
            plik.write(str(wyniki))
    
    

            
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
        x = x * 180/np.pi
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
        M = self.a * (1 - self.e2) / np.sqrt((1 - self.e2 * np.sin(self.flat)**2)**3)
        return(M)
            
            

    def XYZ2BLH(self, plik): 
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
        dane = self.danezpl(plik)
        wynik = []
        for i in dane:
            X, Y, Z = i
        
            p = np.sqrt(X**2 + Y**2)
            f = np.arctan(Z/(p*(1-self.e2)))
            while True:
                N = self.Np(f)
                h = (p / np.cos(f)) - N
                fpop = f
                f = np.arctan(Z/(p*(1-self.e2*(N/(N+h)))))
                if abs(fpop-f) < (0.000001/206265):
                    break
            l = np.arctan2(Y,X)
            wynik.append([degrees(f), degrees(l), h])

        with open('wyniki_XYZ2BLH.txt', 'w') as p:
            p.write('{:^10s} {:^10s} {:^10s} \n'.format('phi[°]','lam[°]','h[m]'))
            for j in wynik:
                p.write('{:^10.3f} {:^10.3f} {:^10.3f}\n'.format(j[0], j[1], j[2]))
        return(wynik)

        
    
    def BLH2XYZ(self, plik):
        """
        Funkcja przeliczająca współrzędne geodezyjne (phi, lam h) na współrzędne ortokartezjańskie (X, Y, Z)

        Parametry:
        ----------
        f : FLOAT
            szerokosć geodezyjna wyrażona w stopniach dziesiętnych
        l : FLOAT
            długosć geodezyjna wyrażona w stopniach dziesiętnych
        h : FLOAT
            wysokosć elipsoidalna wyrażona w metrach

        Zwraca
        -------
        X - [metry]
        Y - [metry]
        Z - [metry]

        """
        dane = self.danezpl(plik)
        wynik = []
        for i in dane:
            f, l, h = i
            N = self.Np(f)

            f = f * np.pi / 180
            l = l * np.pi / 180

            X = (N + h) * np.cos(f) * np.cos(l)
            Y = (N + h) * np.cos(f) * np.sin(l)
            Z = (N * (1 - self.e2) + h) * np.sin(f)
            wynik.append([X, Y, Z])
            
        with open('wyniki_BLH2XYZ.txt', 'w') as p:
            p.write('{:^10s} {:^10s} {:^10s} \n'.format('X[m]','Y[m]','Z[m]'))
            for j in wynik:
                p.write('{:^10.3f} {:^10.3f} {:^10.3f}\n'.format(j[0], j[1], j[2]))
        return(wynik)

    
    def FL21992(self, plik): 
        """
        
        Odwzorowanie Gausa Krugera do układu 1992. Odnosi się do południka osiowego 19 stopni. 
        Współrzędne wejsciowe zostają odwzorowane na do układu lokalnego GK a następnie przeskalowane zgodnie z układem 1992.
      
        Parametry:
        ---------
        f:  FLOAT
        szerokoć geodezyjna wyrażona w radianach
        l:  FLOAT
        długoć geodezyjna wyrażona w radianach
       
        Zwraca:
        ---------
        x:  FLOAT
        szerokosc prostkątna lokalna wyrażona w metrach
        y:  FLOAT
        długosc prostokątna lokalna wyrażona w metrach
        """
        dane = self.danezpl(plik)
        wynik = []
        for i in dane:
            f, l = i
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
            
            wynik.append([x92, y92])
        with open('wyniki_1992.txt', 'w') as p:
            p.write('{:^10s} {:^10s} \n'.format('X 1992[m]','Y 1992[m]'))
            for j in wynik:
                p.write('{:^10.3f} {:^10.3f}\n'.format(j[0], j[1]))
        return(wynik)


    def FL22000(self, plik):
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
     
        Zwraca:
        ---------
        x:  FLOAT
            szerokosc prostkątna lokalna wyrażona w metrach
        y:  FLOAT
            długosc prostokątna lokalna wyrażona w metrach
        """
        dane = self.danezpl(plik)
        wynik = []
        for i in dane:
            f, l = i
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
            wynik.append([x00, y00])

        with open('wyniki_2000.txt', 'w') as p:
            p.write('{:^10s} {:^10s}\n'.format('X 2000[m]','Y 2000[m]'))
            for j in wynik:
                p.write('{:^10.3f} {:^10.3f}\n'.format(j[0], j[1]))
        return(wynik)

    
    def XYZ2NEU(self, plik): 
    
        """
        Na podstawie podanych parametrów tworzony jest wektor obserwacji oraz macierz obrotu czyli szukane wektory n e u.
        Parametry:
        ---------
        Xp, Yp, Zp:  FLOAT
            współrzędne początku odcinka w ukłdzaie orto - kartezjańskim
        Xp, Yp, Zp:  FLOAT
            współrzędne końca odcinka w ukłdzaie orto - kartezjańskim
       
    
        Zwraca:
        ---------
        n, e u: FLOAT
            wektory przestrzenne
        """
        dane = self.danezpl(plik)
        wynik = []
        for i in dane:
            xp, yp, zp, xk, yk, zk = i
            p = np.sqrt(xp**2 + yp**2)
            f = np.arctan(zp/(p * (1-self.e2)))
            while True:
                N = self.a/np.sqrt(1-self.e2 * np.sin(f)**2)
                h = (p / np.cos(f)) - N
                fpop = f
                f = np.arctan(zp/(p*(1-self.e2*(N/(N+h)))))
                if np.abs(fpop-f) < (0.000001/206265):
                    break
                l = np.arctan2(yp, xp)
        
            R = np.array([[-np.sin(f) * np.cos(l), -np.sin(l), np.cos(f) * np.cos(l)],
                          [-np.sin(f) * np.sin(l), np.cos(l), np.cos(f) * np.sin(l)],
                          [np.cos(f), 0, np.sin(f)]])
        
            
            dXYZ = np.array([[xk - xp],[yk - yp],[zk - zp]])
            neu = R.T @ dXYZ
            wynik.append([neu[0][0], neu[1][0],neu[2][0]])
        
        with open('wyniki_XYZ2NEU.txt', 'w') as p:
            p.write( '{:^15s} {:^15s} {:^15s}\n'.format('n','e','u'))
            for j in wynik:
                p.write(' {:^15.3f} {:^15.3f} {:^15.3f}\n'.format(j[0], j[1], j[2]))
        return(wynik)
            



if __name__ == "__main__":
    
    ap = ArgumentParser()
  
    ap.add_argument('-plik', type = str, help = 'Podaj nazwę pliku wraz zrozszerzeniem lub scieżkę do pliku.')
    ap.add_argument('-transformacja', type = str, help = 'Wybrana transformacja (XYZ2flh, flh2XYZ, u1992, u2000, XYZ2NEU)')
    ap.add_argument('-odniesienie', type = str, help = 'Przyjmuje model elipsoidy (WGS84, GRS80, krasowski)')
    
    arg = ap.parse_args()
    transformacje_wsp = {'XYZ2BLH':'XYZ2BLH','BLH2XYZ':'BLH2XYZ', 'FL21992':'FL21992', 'FL22000':'FL22000', 'XYZ2NEU':'XYZ2NEU'}
    
    stop = ""
    
    try:
        while stop != "STOP":
            if arg.plik == None:
                arg.plik = input(str('Podaj lokalizację pliku txt:'))
            if arg.transformacja == None:
                arg.transformacja = input(str('Transformacja:')).upper()
            if arg.odniesienie == None:
                arg.odniesienie = input(str('Model elipsoidy:')).upper()
            elip = transformacje()
            trans = transformacje_wsp[arg.transformacja]
            if trans == 'XYZ2BLH':
                zapytaj = elip.XYZ2BLH(arg.plik)
            if trans == 'BLH2XYZ':
                zapytaj = elip.BLH2XYZ(arg.plik)
            if trans == 'FL21992':
                zapytaj = elip.FL21992(arg.plik)
            if trans == 'FL22000':
                zapytaj = elip.FL22000(arg.plik)
            if trans == 'XYZ2NEU':
                zapytaj = elip.XYZ2NEU(arg.plik)
                
            print('Raport został zapisany w folderze')
            
            stop = input(str("Aby zakończyć wpisz STOP. Aby korzystać dalej napisz inne słowo.")).upper()
                
            arg.plik = None
            arg.transformacja = None
            arg.odniesienie = None
            
    except FileNotFoundError:
        print('Nie znaleziono pliku.')
    except IndexError:
        print('Format danych jest niepoprawny.')
    except ValueError:
        print('Format danych jest niepoprawny.')
    except KeyError:
        print('Niewlasciwe parametry.')

    finally:
        print('Program zakończył pracę.')
        


