-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: serwis
-- ------------------------------------------------------
-- Server version	8.0.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `czesci`
--

DROP TABLE IF EXISTS `czesci`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `czesci` (
  `id_czesci` int NOT NULL AUTO_INCREMENT,
  `nazwa_czesci` varchar(255) NOT NULL,
  `typ_czesci` int DEFAULT NULL,
  `producent` varchar(255) DEFAULT NULL,
  `numer_katalogowy` varchar(50) DEFAULT NULL,
  `cena_katalogowa` decimal(10,2) DEFAULT NULL,
  `ilosc_dostepna` int DEFAULT NULL,
  PRIMARY KEY (`id_czesci`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `czesci`
--

LOCK TABLES `czesci` WRITE;
/*!40000 ALTER TABLE `czesci` DISABLE KEYS */;
INSERT INTO `czesci` VALUES (1,'Ryzen 7 7800X3D',1,'AMD','24',1399.00,8);
/*!40000 ALTER TABLE `czesci` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `czesci_wykorzystane`
--

DROP TABLE IF EXISTS `czesci_wykorzystane`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `czesci_wykorzystane` (
  `id_pozycji` int NOT NULL AUTO_INCREMENT,
  `id_zlecenia` int NOT NULL,
  `id_czesci` int NOT NULL,
  `ilosc` int NOT NULL,
  `cena_jednostkowa` decimal(10,2) NOT NULL,
  `data_wykorzystania` datetime DEFAULT NULL,
  PRIMARY KEY (`id_pozycji`),
  KEY `id_zlecenia` (`id_zlecenia`),
  KEY `id_czesci` (`id_czesci`),
  CONSTRAINT `czesci_wykorzystane_ibfk_1` FOREIGN KEY (`id_zlecenia`) REFERENCES `zlecenia_naprawy` (`id_zlecenia`),
  CONSTRAINT `czesci_wykorzystane_ibfk_2` FOREIGN KEY (`id_czesci`) REFERENCES `czesci` (`id_czesci`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `czesci_wykorzystane`
--

LOCK TABLES `czesci_wykorzystane` WRITE;
/*!40000 ALTER TABLE `czesci_wykorzystane` DISABLE KEYS */;
/*!40000 ALTER TABLE `czesci_wykorzystane` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `dane_kadrowe`
--

DROP TABLE IF EXISTS `dane_kadrowe`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dane_kadrowe` (
  `id_uzytkownika` int NOT NULL,
  `pesel` varchar(11) NOT NULL,
  `nr_konta` varchar(26) DEFAULT NULL,
  `adres_zamieszkania` varchar(255) DEFAULT NULL,
  `stawka_godzinowa` decimal(10,2) DEFAULT NULL,
  `data_zatrudnienia` date DEFAULT NULL,
  PRIMARY KEY (`id_uzytkownika`),
  UNIQUE KEY `pesel` (`pesel`),
  CONSTRAINT `dane_kadrowe_ibfk_1` FOREIGN KEY (`id_uzytkownika`) REFERENCES `uzytkownicy` (`id_uzytkownika`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dane_kadrowe`
--

LOCK TABLES `dane_kadrowe` WRITE;
/*!40000 ALTER TABLE `dane_kadrowe` DISABLE KEYS */;
/*!40000 ALTER TABLE `dane_kadrowe` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `klienci`
--

DROP TABLE IF EXISTS `klienci`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `klienci` (
  `id_klienta` int NOT NULL AUTO_INCREMENT,
  `imie` varchar(255) DEFAULT NULL,
  `nazwisko` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `nr_telefonu` varchar(20) DEFAULT NULL,
  `adres` varchar(255) DEFAULT NULL,
  `data_rejestracji` datetime DEFAULT NULL,
  `czy_aktywny` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id_klienta`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `klienci`
--

LOCK TABLES `klienci` WRITE;
/*!40000 ALTER TABLE `klienci` DISABLE KEYS */;
INSERT INTO `klienci` VALUES (1,'Jan Kowalski',NULL,'jan@test.pl',NULL,NULL,'2025-12-14 22:45:31',1),(2,NULL,NULL,'jankowal@example.com',NULL,NULL,'2025-12-14 23:04:57',1),(3,'Milosz','Gulasz','miloszg@abc.com','123454321','Warszawa, ul. Polska','2026-01-20 01:39:59',NULL),(4,'Patryk','Kwadrat','pankwadracik@gmail.com','987654321','Kwadratowo, ul. Prostokatna 12','2026-01-20 01:43:56',NULL),(5,'Anna','Kubek','akubek@op.pl','785172216','Wrocław, ul. Opolska 49','2026-01-20 02:36:38',NULL);
/*!40000 ALTER TABLE `klienci` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pozycje_zamowienia`
--

DROP TABLE IF EXISTS `pozycje_zamowienia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pozycje_zamowienia` (
  `id_pozycji` int NOT NULL AUTO_INCREMENT,
  `id_zamowienia` int NOT NULL,
  `id_czesci` int NOT NULL,
  `ilosc` int NOT NULL,
  `cena_jednostkowa` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id_pozycji`),
  KEY `id_zamowienia` (`id_zamowienia`),
  KEY `id_czesci` (`id_czesci`),
  CONSTRAINT `pozycje_zamowienia_ibfk_1` FOREIGN KEY (`id_zamowienia`) REFERENCES `zamowienia_czesci` (`id_zamowienia`),
  CONSTRAINT `pozycje_zamowienia_ibfk_2` FOREIGN KEY (`id_czesci`) REFERENCES `czesci` (`id_czesci`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pozycje_zamowienia`
--

LOCK TABLES `pozycje_zamowienia` WRITE;
/*!40000 ALTER TABLE `pozycje_zamowienia` DISABLE KEYS */;
/*!40000 ALTER TABLE `pozycje_zamowienia` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `role`
--

DROP TABLE IF EXISTS `role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `role` (
  `id_rola` int NOT NULL AUTO_INCREMENT,
  `nazwa_rola` varchar(100) NOT NULL,
  PRIMARY KEY (`id_rola`),
  UNIQUE KEY `nazwa_rola` (`nazwa_rola`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role`
--

LOCK TABLES `role` WRITE;
/*!40000 ALTER TABLE `role` DISABLE KEYS */;
INSERT INTO `role` VALUES (1,'administrator'),(2,'manager'),(3,'pracownik');
/*!40000 ALTER TABLE `role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `statusy_zamowien`
--

DROP TABLE IF EXISTS `statusy_zamowien`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `statusy_zamowien` (
  `id_statusu` int NOT NULL AUTO_INCREMENT,
  `nazwa_statusu` varchar(100) NOT NULL,
  PRIMARY KEY (`id_statusu`),
  UNIQUE KEY `nazwa_statusu` (`nazwa_statusu`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `statusy_zamowien`
--

LOCK TABLES `statusy_zamowien` WRITE;
/*!40000 ALTER TABLE `statusy_zamowien` DISABLE KEYS */;
INSERT INTO `statusy_zamowien` VALUES (1,'Do zatwierdzenia'),(5,'Dostarczone'),(3,'W realizacji'),(4,'Wysłane'),(2,'Zatwierdzone');
/*!40000 ALTER TABLE `statusy_zamowien` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `statusy_zlecen`
--

DROP TABLE IF EXISTS `statusy_zlecen`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `statusy_zlecen` (
  `id_statusu` int NOT NULL AUTO_INCREMENT,
  `nazwa_statusu` varchar(100) NOT NULL,
  PRIMARY KEY (`id_statusu`),
  UNIQUE KEY `nazwa_statusu` (`nazwa_statusu`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `statusy_zlecen`
--

LOCK TABLES `statusy_zlecen` WRITE;
/*!40000 ALTER TABLE `statusy_zlecen` DISABLE KEYS */;
INSERT INTO `statusy_zlecen` VALUES (4,'Gotowe'),(3,'Oczekuje na części'),(1,'Przyjęte'),(2,'W naprawie'),(5,'Zakończone'),(6,'Zarchiwizowane');
/*!40000 ALTER TABLE `statusy_zlecen` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `typy_czesci`
--

DROP TABLE IF EXISTS `typy_czesci`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `typy_czesci` (
  `id_typu` int NOT NULL AUTO_INCREMENT,
  `nazwa_typu` varchar(50) NOT NULL,
  PRIMARY KEY (`id_typu`),
  UNIQUE KEY `nazwa_typu` (`nazwa_typu`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `typy_czesci`
--

LOCK TABLES `typy_czesci` WRITE;
/*!40000 ALTER TABLE `typy_czesci` DISABLE KEYS */;
INSERT INTO `typy_czesci` VALUES (10,'Akcesoria'),(8,'Chłodzenie'),(4,'Dysk Twardy'),(9,'Ekran'),(11,'Inne'),(5,'Karta Graficzna'),(7,'Obudowa'),(3,'Pamięć RAM'),(2,'Płyta Główna'),(1,'Procesor'),(6,'Zasilacz');
/*!40000 ALTER TABLE `typy_czesci` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `typy_sprzetu`
--

DROP TABLE IF EXISTS `typy_sprzetu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `typy_sprzetu` (
  `id_typu` int NOT NULL AUTO_INCREMENT,
  `nazwa_typu` varchar(255) NOT NULL,
  PRIMARY KEY (`id_typu`),
  UNIQUE KEY `nazwa_typu` (`nazwa_typu`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `typy_sprzetu`
--

LOCK TABLES `typy_sprzetu` WRITE;
/*!40000 ALTER TABLE `typy_sprzetu` DISABLE KEYS */;
INSERT INTO `typy_sprzetu` VALUES (4,'Drukarka'),(3,'Komputer PC'),(1,'Laptop'),(2,'Telefon');
/*!40000 ALTER TABLE `typy_sprzetu` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `uzytkownicy`
--

DROP TABLE IF EXISTS `uzytkownicy`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `uzytkownicy` (
  `id_uzytkownika` int NOT NULL AUTO_INCREMENT,
  `imie` varchar(255) NOT NULL,
  `nazwisko` varchar(255) NOT NULL,
  `login` varchar(255) NOT NULL,
  `haslo_hash` varchar(255) NOT NULL,
  `email` varchar(255) DEFAULT NULL,
  `nr_telefonu` varchar(20) DEFAULT NULL,
  `rola_uzytkownika` int DEFAULT NULL,
  `czy_aktywny` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id_uzytkownika`),
  UNIQUE KEY `login` (`login`),
  UNIQUE KEY `email` (`email`),
  KEY `rola_uzytkownika` (`rola_uzytkownika`),
  CONSTRAINT `uzytkownicy_ibfk_1` FOREIGN KEY (`rola_uzytkownika`) REFERENCES `role` (`id_rola`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `uzytkownicy`
--

LOCK TABLES `uzytkownicy` WRITE;
/*!40000 ALTER TABLE `uzytkownicy` DISABLE KEYS */;
INSERT INTO `uzytkownicy` VALUES (1,'employee1','employee1','employee1','$2b$12$O3OYoUyRTP1UuovldHOYsO.Xk9rsVCheIdi/8umU2cozeI3WZEWqO',NULL,NULL,NULL,1),(3,'Admin','Systemowy','admin','scrypt:32768:8:1$AWfL1ZG6hPxdzjju$4af9cf6721540227e844a3326f9e37f58504f59290e83081d5fe0af7bce47c97b1cb5b8a20db57a61651e9125717d3b1bc7299b10707c90175c60eb4c3ef97c7','admin@serwis.pl','123456789',1,1),(4,'Pracownik','Firmowy','pracownik','scrypt:32768:8:1$46SIv7Za9fzUFuBZ$432a646ee07722c5717a281e9b5604996ef252f681a6a585ec58dbd8f3e16e85ab6d218c54b20cd6c843640307d90c9906fde810b8fea84cbd03ae2a6b7ea24d','pracownik@serwis.pl','312345678',3,1),(5,'Kierownik','Kierowniczy','kierownik','scrypt:32768:8:1$roSLOd9d0EQY1Qjw$31371b7b60cf37580be34cd646e019c4c4e2c2b47fd4dc9a7dbac6c23a2553374d2e0c2dc213673c8ca17775fef0862062b1dc75c63a47495f2cee71721ccf59','kierownik@serwis.pl','212345678',2,1);
/*!40000 ALTER TABLE `uzytkownicy` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `zamowienia_czesci`
--

DROP TABLE IF EXISTS `zamowienia_czesci`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `zamowienia_czesci` (
  `id_zamowienia` int NOT NULL AUTO_INCREMENT,
  `id_skladajacego` int NOT NULL,
  `id_zatwierdzajacego` int DEFAULT NULL,
  `data_zlozenia` datetime DEFAULT NULL,
  `data_zatwierdzenia` datetime DEFAULT NULL,
  `data_realizacji` datetime DEFAULT NULL,
  `status_zamowienia` int NOT NULL,
  PRIMARY KEY (`id_zamowienia`),
  KEY `id_skladajacego` (`id_skladajacego`),
  KEY `id_zatwierdzajacego` (`id_zatwierdzajacego`),
  KEY `status_zamowienia` (`status_zamowienia`),
  CONSTRAINT `zamowienia_czesci_ibfk_1` FOREIGN KEY (`id_skladajacego`) REFERENCES `uzytkownicy` (`id_uzytkownika`),
  CONSTRAINT `zamowienia_czesci_ibfk_2` FOREIGN KEY (`id_zatwierdzajacego`) REFERENCES `uzytkownicy` (`id_uzytkownika`),
  CONSTRAINT `zamowienia_czesci_ibfk_3` FOREIGN KEY (`status_zamowienia`) REFERENCES `statusy_zamowien` (`id_statusu`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `zamowienia_czesci`
--

LOCK TABLES `zamowienia_czesci` WRITE;
/*!40000 ALTER TABLE `zamowienia_czesci` DISABLE KEYS */;
/*!40000 ALTER TABLE `zamowienia_czesci` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `zlecenia_naprawy`
--

DROP TABLE IF EXISTS `zlecenia_naprawy`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `zlecenia_naprawy` (
  `id_zlecenia` int NOT NULL AUTO_INCREMENT,
  `id_klienta` int NOT NULL,
  `id_pracownika` int NOT NULL,
  `typ_sprzetu` int NOT NULL,
  `data_rozpoczecia` datetime DEFAULT NULL,
  `data_zakonczenia` datetime DEFAULT NULL,
  `opis_usterki` varchar(2000) DEFAULT NULL,
  `status_zlecenia` int NOT NULL,
  `koszt_robocizny` decimal(10,2) DEFAULT NULL,
  `koszt_czesci` decimal(10,2) DEFAULT NULL,
  `marka_sprzetu` varchar(255) DEFAULT NULL,
  `model_sprzetu` varchar(255) DEFAULT NULL,
  `numer_seryjny` varchar(50) DEFAULT NULL,
  `diagnoza` varchar(255) DEFAULT NULL,
  `wykonane_czynnosci` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_zlecenia`),
  KEY `id_klienta` (`id_klienta`),
  KEY `id_pracownika` (`id_pracownika`),
  KEY `typ_sprzetu` (`typ_sprzetu`),
  KEY `status_zlecenia` (`status_zlecenia`),
  CONSTRAINT `zlecenia_naprawy_ibfk_1` FOREIGN KEY (`id_klienta`) REFERENCES `klienci` (`id_klienta`),
  CONSTRAINT `zlecenia_naprawy_ibfk_2` FOREIGN KEY (`id_pracownika`) REFERENCES `uzytkownicy` (`id_uzytkownika`),
  CONSTRAINT `zlecenia_naprawy_ibfk_3` FOREIGN KEY (`typ_sprzetu`) REFERENCES `typy_sprzetu` (`id_typu`),
  CONSTRAINT `zlecenia_naprawy_ibfk_4` FOREIGN KEY (`status_zlecenia`) REFERENCES `statusy_zlecen` (`id_statusu`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `zlecenia_naprawy`
--

LOCK TABLES `zlecenia_naprawy` WRITE;
/*!40000 ALTER TABLE `zlecenia_naprawy` DISABLE KEYS */;
INSERT INTO `zlecenia_naprawy` VALUES (1,3,1,3,'2026-01-20 00:00:00',NULL,'Komputer zawiesza sie zaraz po uruchomieniu. Blad wystepuje przy restartach i po tym jak komputer byl wczesniej uruchomiony. Przy starcie zimnym blad nie wystepuje.',2,0.00,0.00,'','','','Źle podłączona pamięć RAM.',''),(2,1,3,1,'2026-01-20 03:19:15',NULL,'',6,0.00,0.00,NULL,NULL,NULL,NULL,NULL),(3,4,4,4,'2026-01-20 03:21:58',NULL,'Drukarka nie może się podłączyć do sieci bezprzewodowej.',1,0.00,0.00,NULL,NULL,NULL,NULL,NULL),(4,5,4,2,'2000-01-01 00:00:00',NULL,'Bateria bardzo szybko się rozładowuje.',1,0.00,0.00,'Apple','iPhone 8','','','');
/*!40000 ALTER TABLE `zlecenia_naprawy` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-01-25 18:47:26
