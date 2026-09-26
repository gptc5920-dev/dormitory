-- MySQL dump 10.13  Distrib 8.4.9, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: dormitory
-- ------------------------------------------------------
-- Server version	8.4.9

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `accounts_referencesequence`
--

DROP TABLE IF EXISTS `accounts_referencesequence`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accounts_referencesequence` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `key` varchar(80) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `value` bigint unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `key` (`key`),
  CONSTRAINT `accounts_referencesequence_chk_1` CHECK ((`value` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_referencesequence`
--

LOCK TABLES `accounts_referencesequence` WRITE;
/*!40000 ALTER TABLE `accounts_referencesequence` DISABLE KEYS */;
INSERT INTO `accounts_referencesequence` VALUES (1,'monitoring.incident:INC-2026-',8);
/*!40000 ALTER TABLE `accounts_referencesequence` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accounts_user`
--

DROP TABLE IF EXISTS `accounts_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accounts_user` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `password` varchar(128) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `first_name` varchar(150) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `last_name` varchar(150) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `email` varchar(254) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `role` varchar(20) COLLATE utf8mb4_0900_as_cs NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_user`
--

LOCK TABLES `accounts_user` WRITE;
/*!40000 ALTER TABLE `accounts_user` DISABLE KEYS */;
INSERT INTO `accounts_user` VALUES (1,'pbkdf2_sha256$1500000$C9QbrQeOo9gL62E5aqzGf1$s4p5zkBjjCUXrDoTlvNgfPPkSKlqwkSlq2XPKH6LJdE=',NULL,0,'manager','Dormitory','Manager','manager@example.test',0,1,'2026-08-18 10:50:32.258000','manager'),(2,'pbkdf2_sha256$1500000$lUlfzvJkpsgaTKZaHup3y1$60XN26mgxOW6BnBDe3zJ6BFzRcttuWmSzgmpc28Y/P8=',NULL,1,'admin','System','Administrator','admin@example.test',1,1,'2026-08-18 10:50:34.675000','admin');
/*!40000 ALTER TABLE `accounts_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accounts_user_groups`
--

DROP TABLE IF EXISTS `accounts_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accounts_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `accounts_user_groups_user_id_group_id_59c0b32f_uniq` (`user_id`,`group_id`),
  KEY `accounts_user_groups_group_id_bd11a704_fk_auth_group_id` (`group_id`),
  CONSTRAINT `accounts_user_groups_group_id_bd11a704_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `accounts_user_groups_user_id_52b62117_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_user_groups`
--

LOCK TABLES `accounts_user_groups` WRITE;
/*!40000 ALTER TABLE `accounts_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `accounts_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accounts_user_user_permissions`
--

DROP TABLE IF EXISTS `accounts_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accounts_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `accounts_user_user_permi_user_id_permission_id_2ab516c2_uniq` (`user_id`,`permission_id`),
  KEY `accounts_user_user_p_permission_id_113bb443_fk_auth_perm` (`permission_id`),
  CONSTRAINT `accounts_user_user_p_permission_id_113bb443_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `accounts_user_user_p_user_id_e4f0a161_fk_accounts_` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_user_user_permissions`
--

LOCK TABLES `accounts_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `accounts_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `accounts_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) COLLATE utf8mb4_0900_as_cs NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) COLLATE utf8mb4_0900_as_cs NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=73 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add content type',4,'add_contenttype'),(14,'Can change content type',4,'change_contenttype'),(15,'Can delete content type',4,'delete_contenttype'),(16,'Can view content type',4,'view_contenttype'),(17,'Can add session',5,'add_session'),(18,'Can change session',5,'change_session'),(19,'Can delete session',5,'delete_session'),(20,'Can view session',5,'view_session'),(21,'Can add Token',6,'add_token'),(22,'Can change Token',6,'change_token'),(23,'Can delete Token',6,'delete_token'),(24,'Can view Token',6,'view_token'),(25,'Can add Token',7,'add_tokenproxy'),(26,'Can change Token',7,'change_tokenproxy'),(27,'Can delete Token',7,'delete_tokenproxy'),(28,'Can view Token',7,'view_tokenproxy'),(29,'Can add user',8,'add_user'),(30,'Can change user',8,'change_user'),(31,'Can delete user',8,'delete_user'),(32,'Can view user',8,'view_user'),(33,'Can add reference sequence',9,'add_referencesequence'),(34,'Can change reference sequence',9,'change_referencesequence'),(35,'Can delete reference sequence',9,'delete_referencesequence'),(36,'Can view reference sequence',9,'view_referencesequence'),(37,'Can add room',10,'add_room'),(38,'Can change room',10,'change_room'),(39,'Can delete room',10,'delete_room'),(40,'Can view room',10,'view_room'),(41,'Can add tenant',11,'add_tenant'),(42,'Can change tenant',11,'change_tenant'),(43,'Can delete tenant',11,'delete_tenant'),(44,'Can view tenant',11,'view_tenant'),(45,'Can add detection cooldown',12,'add_detectioncooldown'),(46,'Can change detection cooldown',12,'change_detectioncooldown'),(47,'Can delete detection cooldown',12,'delete_detectioncooldown'),(48,'Can view detection cooldown',12,'view_detectioncooldown'),(49,'Can add camera source',13,'add_camerasource'),(50,'Can change camera source',13,'change_camerasource'),(51,'Can delete camera source',13,'delete_camerasource'),(52,'Can view camera source',13,'view_camerasource'),(53,'Can add incident',14,'add_incident'),(54,'Can change incident',14,'change_incident'),(55,'Can delete incident',14,'delete_incident'),(56,'Can view incident',14,'view_incident'),(57,'Can add video job',15,'add_videojob'),(58,'Can change video job',15,'change_videojob'),(59,'Can delete video job',15,'delete_videojob'),(60,'Can view video job',15,'view_videojob'),(61,'Can add dormitory rule',16,'add_dormitoryrule'),(62,'Can change dormitory rule',16,'change_dormitoryrule'),(63,'Can delete dormitory rule',16,'delete_dormitoryrule'),(64,'Can view dormitory rule',16,'view_dormitoryrule'),(65,'Can add violation',17,'add_violation'),(66,'Can change violation',17,'change_violation'),(67,'Can delete violation',17,'delete_violation'),(68,'Can view violation',17,'view_violation'),(69,'Can add warning',18,'add_warning'),(70,'Can change warning',18,'change_warning'),(71,'Can delete warning',18,'delete_warning'),(72,'Can view warning',18,'view_warning');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `authtoken_token`
--

DROP TABLE IF EXISTS `authtoken_token`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `authtoken_token` (
  `key` varchar(40) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `created` datetime(6) NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`key`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `authtoken_token_user_id_35299eff_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `authtoken_token`
--

LOCK TABLES `authtoken_token` WRITE;
/*!40000 ALTER TABLE `authtoken_token` DISABLE KEYS */;
INSERT INTO `authtoken_token` VALUES ('d524a6fec06b2bc76ab944fb95c2d8ae82c0dfc1','2026-09-18 11:13:31.647000',1);
/*!40000 ALTER TABLE `authtoken_token` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext COLLATE utf8mb4_0900_as_cs,
  `object_repr` varchar(200) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext COLLATE utf8mb4_0900_as_cs NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_accounts_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `model` varchar(100) COLLATE utf8mb4_0900_as_cs NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (9,'accounts','referencesequence'),(8,'accounts','user'),(1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(6,'authtoken','token'),(7,'authtoken','tokenproxy'),(4,'contenttypes','contenttype'),(13,'monitoring','camerasource'),(12,'monitoring','detectioncooldown'),(14,'monitoring','incident'),(15,'monitoring','videojob'),(5,'sessions','session'),(10,'tenants','room'),(11,'tenants','tenant'),(16,'violations','dormitoryrule'),(17,'violations','violation'),(18,'violations','warning');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2026-09-23 12:31:06.495149'),(2,'contenttypes','0002_remove_content_type_name','2026-09-23 12:31:06.702959'),(3,'auth','0001_initial','2026-09-23 12:31:07.534582'),(4,'auth','0002_alter_permission_name_max_length','2026-09-23 12:31:07.670160'),(5,'auth','0003_alter_user_email_max_length','2026-09-23 12:31:07.683747'),(6,'auth','0004_alter_user_username_opts','2026-09-23 12:31:07.696351'),(7,'auth','0005_alter_user_last_login_null','2026-09-23 12:31:07.707561'),(8,'auth','0006_require_contenttypes_0002','2026-09-23 12:31:07.712200'),(9,'auth','0007_alter_validators_add_error_messages','2026-09-23 12:31:07.728197'),(10,'auth','0008_alter_user_username_max_length','2026-09-23 12:31:07.740386'),(11,'auth','0009_alter_user_last_name_max_length','2026-09-23 12:31:07.752271'),(12,'auth','0010_alter_group_name_max_length','2026-09-23 12:31:07.780993'),(13,'auth','0011_update_proxy_permissions','2026-09-23 12:31:07.795577'),(14,'auth','0012_alter_user_first_name_max_length','2026-09-23 12:31:07.806979'),(15,'accounts','0001_initial','2026-09-23 12:31:08.539894'),(16,'accounts','0002_referencesequence','2026-09-23 12:31:08.621729'),(17,'admin','0001_initial','2026-09-23 12:31:08.950045'),(18,'admin','0002_logentry_remove_auto_add','2026-09-23 12:31:08.964122'),(19,'admin','0003_logentry_add_action_flag_choices','2026-09-23 12:31:08.979116'),(20,'authtoken','0001_initial','2026-09-23 12:31:09.184558'),(21,'authtoken','0002_auto_20160226_1747','2026-09-23 12:31:09.234734'),(22,'authtoken','0003_tokenproxy','2026-09-23 12:31:09.240944'),(23,'authtoken','0004_alter_tokenproxy_options','2026-09-23 12:31:09.254223'),(24,'tenants','0001_initial','2026-09-23 12:31:09.510693'),(25,'monitoring','0001_initial','2026-09-23 12:31:11.061656'),(26,'monitoring','0002_incident_query_indexes','2026-09-23 12:31:11.287507'),(27,'sessions','0001_initial','2026-09-23 12:31:11.357415'),(28,'violations','0001_initial','2026-09-23 12:31:12.678263'),(29,'violations','0002_record_date_indexes','2026-09-23 12:31:12.783094');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `session_data` longtext COLLATE utf8mb4_0900_as_cs NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `monitoring_camerasource`
--

DROP TABLE IF EXISTS `monitoring_camerasource`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `monitoring_camerasource` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(120) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `source_type` varchar(20) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `location` varchar(160) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `stream_url` varchar(500) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `is_enabled` tinyint(1) NOT NULL,
  `room_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `monitoring_camerasource_room_id_b600a837_fk_tenants_room_id` (`room_id`),
  CONSTRAINT `monitoring_camerasource_room_id_b600a837_fk_tenants_room_id` FOREIGN KEY (`room_id`) REFERENCES `tenants_room` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `monitoring_camerasource`
--

LOCK TABLES `monitoring_camerasource` WRITE;
/*!40000 ALTER TABLE `monitoring_camerasource` DISABLE KEYS */;
INSERT INTO `monitoring_camerasource` VALUES (1,'Lobby browser camera','webcam','Main lobby','',1,NULL),(2,'room 1','webcam','ground floor','',1,1),(3,'exit','webcam','first floor','',1,NULL);
/*!40000 ALTER TABLE `monitoring_camerasource` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `monitoring_detectioncooldown`
--

DROP TABLE IF EXISTS `monitoring_detectioncooldown`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `monitoring_detectioncooldown` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `key` varchar(255) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `last_triggered_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `key` (`key`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `monitoring_detectioncooldown`
--

LOCK TABLES `monitoring_detectioncooldown` WRITE;
/*!40000 ALTER TABLE `monitoring_detectioncooldown` DISABLE KEYS */;
INSERT INTO `monitoring_detectioncooldown` VALUES (1,'live:3:none:possible_smoke','2026-09-24 08:05:43.220853');
/*!40000 ALTER TABLE `monitoring_detectioncooldown` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `monitoring_incident`
--

DROP TABLE IF EXISTS `monitoring_incident`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `monitoring_incident` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `reference` varchar(20) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `incident_type` varchar(30) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `confidence` double DEFAULT NULL,
  `details` longtext COLLATE utf8mb4_0900_as_cs NOT NULL,
  `detected_labels` json NOT NULL,
  `occurred_at` datetime(6) NOT NULL,
  `snapshot` varchar(100) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `source_name` varchar(160) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `verified_at` datetime(6) DEFAULT NULL,
  `review_notes` longtext COLLATE utf8mb4_0900_as_cs NOT NULL,
  `assigned_tenant_id` bigint DEFAULT NULL,
  `room_id` bigint DEFAULT NULL,
  `source_id` bigint DEFAULT NULL,
  `verified_by_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `reference` (`reference`),
  KEY `monitoring_incident_assigned_tenant_id_cdc16b3f_fk_tenants_t` (`assigned_tenant_id`),
  KEY `monitoring_incident_room_id_d3ef2a01_fk_tenants_room_id` (`room_id`),
  KEY `monitoring_incident_source_id_47a4fe67_fk_monitorin` (`source_id`),
  KEY `monitoring_incident_verified_by_id_6de720cb_fk_accounts_user_id` (`verified_by_id`),
  KEY `monitoring_incident_occurred_at_c54c222e` (`occurred_at`),
  KEY `monitoring_incident_status_ca4e146a` (`status`),
  CONSTRAINT `monitoring_incident_assigned_tenant_id_cdc16b3f_fk_tenants_t` FOREIGN KEY (`assigned_tenant_id`) REFERENCES `tenants_tenant` (`id`),
  CONSTRAINT `monitoring_incident_room_id_d3ef2a01_fk_tenants_room_id` FOREIGN KEY (`room_id`) REFERENCES `tenants_room` (`id`),
  CONSTRAINT `monitoring_incident_source_id_47a4fe67_fk_monitorin` FOREIGN KEY (`source_id`) REFERENCES `monitoring_camerasource` (`id`),
  CONSTRAINT `monitoring_incident_verified_by_id_6de720cb_fk_accounts_user_id` FOREIGN KEY (`verified_by_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `monitoring_incident`
--

LOCK TABLES `monitoring_incident` WRITE;
/*!40000 ALTER TABLE `monitoring_incident` DISABLE KEYS */;
INSERT INTO `monitoring_incident` VALUES (1,'INC-2026-0001','manual','assigned',NULL,'Sample verified quiet-hours report.','[]','2026-08-18 10:50:37.244000','','Lobby browser camera','2026-08-18 10:50:37.242000','Seeded manager verification.',1,1,1,1),(2,'INC-2026-0002','bottle','assigned',NULL,'FGFGN','[]','2026-08-19 09:37:45.899000','','','2026-09-24 07:39:07.657312','warning 1',1,1,NULL,1),(3,'INC-2026-0003','person','dismissed',NULL,'tenant','[]','2026-09-18 09:32:32.428000','','','2026-09-18 09:32:52.350000','Dismissed by manager.',NULL,NULL,NULL,1),(4,'INC-2026-0004','possible_smoke','dismissed',0.5434168836805555,'Automated possible smoke visual cue; method: untrained_visual_cue. Manager verification required.','[{\"box\": [194, 0, 769, 438], \"label\": \"possible smoke visual cue\", \"method\": \"untrained_visual_cue\", \"confidence\": 0.543, \"incident_type\": \"possible_smoke\"}]','2026-09-24 07:45:50.842273','incidents/2026/09/INC-2026-0004.jpg','exit','2026-09-24 07:51:44.415867','Dismissed by manager.',NULL,NULL,3,1),(5,'INC-2026-0005','possible_smoke','dismissed',0.497373046875,'Automated possible smoke visual cue; method: untrained_visual_cue. Manager verification required.','[{\"box\": [798, 308, 1197, 612], \"label\": \"possible smoke visual cue\", \"method\": \"untrained_visual_cue\", \"confidence\": 0.497, \"incident_type\": \"possible_smoke\"}]','2026-09-24 07:46:56.784899','incidents/2026/09/INC-2026-0005.jpg','exit',NULL,'Dismissed by manager.',NULL,NULL,3,NULL),(6,'INC-2026-0006','possible_smoke','dismissed',0.7,'Automated possible smoke visual cue; method: untrained_visual_cue. Manager verification required.','[{\"box\": [0, 0, 1280, 612], \"label\": \"possible smoke visual cue\", \"method\": \"untrained_visual_cue\", \"confidence\": 0.7, \"incident_type\": \"possible_smoke\"}]','2026-09-24 07:48:35.779907','incidents/2026/09/INC-2026-0006.jpg','exit',NULL,'Dismissed by manager.',NULL,NULL,3,NULL),(7,'INC-2026-0007','possible_smoke','dismissed',0.5052484809027777,'Automated possible smoke visual cue; method: untrained_visual_cue. Manager verification required.','[{\"box\": [778, 0, 1048, 612], \"label\": \"possible smoke visual cue\", \"method\": \"untrained_visual_cue\", \"confidence\": 0.505, \"incident_type\": \"possible_smoke\"}]','2026-09-24 07:49:35.784562','incidents/2026/09/INC-2026-0007.jpg','exit',NULL,'Dismissed by manager.',NULL,NULL,3,NULL),(8,'INC-2026-0008','possible_smoke','new',0.5137554253472223,'Automated possible smoke visual cue; method: untrained_visual_cue. Manager verification required.','[{\"box\": [1008, 111, 1280, 612], \"label\": \"possible smoke visual cue\", \"method\": \"untrained_visual_cue\", \"confidence\": 0.514, \"incident_type\": \"possible_smoke\"}]','2026-09-24 08:05:43.262688','incidents/2026/09/INC-2026-0008.jpg','exit',NULL,'',NULL,NULL,3,NULL);
/*!40000 ALTER TABLE `monitoring_incident` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `monitoring_videojob`
--

DROP TABLE IF EXISTS `monitoring_videojob`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `monitoring_videojob` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `video` varchar(100) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `source_name` varchar(160) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `frames_processed` int unsigned NOT NULL,
  `incidents_created` int unsigned NOT NULL,
  `error` longtext COLLATE utf8mb4_0900_as_cs NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `completed_at` datetime(6) DEFAULT NULL,
  `created_by_id` bigint NOT NULL,
  `room_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `monitoring_videojob_created_by_id_93e8e576_fk_accounts_user_id` (`created_by_id`),
  KEY `monitoring_videojob_room_id_14c53456_fk_tenants_room_id` (`room_id`),
  CONSTRAINT `monitoring_videojob_created_by_id_93e8e576_fk_accounts_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `monitoring_videojob_room_id_14c53456_fk_tenants_room_id` FOREIGN KEY (`room_id`) REFERENCES `tenants_room` (`id`),
  CONSTRAINT `monitoring_videojob_chk_1` CHECK ((`frames_processed` >= 0)),
  CONSTRAINT `monitoring_videojob_chk_2` CHECK ((`incidents_created` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `monitoring_videojob`
--

LOCK TABLES `monitoring_videojob` WRITE;
/*!40000 ALTER TABLE `monitoring_videojob` DISABLE KEYS */;
INSERT INTO `monitoring_videojob` VALUES (1,'uploads/videos/2026/09/videoplayback.mp4','Uploaded corridor video','completed',12,0,'','2026-09-18 10:02:49.860000','2026-09-18 10:02:50.681000',1,NULL),(2,'uploads/videos/2026/09/videoplayback_TDPF3os.mp4','Uploaded corridor video','completed',12,0,'','2026-09-18 10:02:56.111000','2026-09-18 10:02:56.512000',1,NULL),(3,'uploads/videos/2026/09/videoplayback_hJXrO7j.mp4','Uploaded corridor video','completed',12,0,'','2026-09-18 10:03:51.051000','2026-09-18 10:03:51.448000',1,NULL);
/*!40000 ALTER TABLE `monitoring_videojob` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenants_room`
--

DROP TABLE IF EXISTS `tenants_room`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tenants_room` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `number` varchar(20) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `floor` smallint unsigned NOT NULL,
  `capacity` smallint unsigned NOT NULL,
  `description` varchar(255) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `number` (`number`),
  CONSTRAINT `tenants_room_chk_1` CHECK ((`floor` >= 0)),
  CONSTRAINT `tenants_room_chk_2` CHECK ((`capacity` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenants_room`
--

LOCK TABLES `tenants_room` WRITE;
/*!40000 ALTER TABLE `tenants_room` DISABLE KEYS */;
INSERT INTO `tenants_room` VALUES (1,'101',1,4,'East wing',1),(2,'102',1,3,'East wing',1),(3,'201',2,4,'North wing',1),(4,'room',6,4,'For Girls only',1),(5,'Room',6,6,'',1);
/*!40000 ALTER TABLE `tenants_room` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenants_tenant`
--

DROP TABLE IF EXISTS `tenants_tenant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tenants_tenant` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `reference` varchar(20) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `first_name` varchar(100) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `last_name` varchar(100) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `email` varchar(254) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `phone` varchar(30) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `emergency_contact` varchar(150) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `enrolled_on` date NOT NULL,
  `move_in_date` date DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `notes` longtext COLLATE utf8mb4_0900_as_cs NOT NULL,
  `room_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `reference` (`reference`),
  KEY `tenants_tenant_room_id_b6c0e1ce_fk_tenants_room_id` (`room_id`),
  CONSTRAINT `tenants_tenant_room_id_b6c0e1ce_fk_tenants_room_id` FOREIGN KEY (`room_id`) REFERENCES `tenants_room` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenants_tenant`
--

LOCK TABLES `tenants_tenant` WRITE;
/*!40000 ALTER TABLE `tenants_tenant` DISABLE KEYS */;
INSERT INTO `tenants_tenant` VALUES (1,'TEN-2026-0001','Jordan','Lee','jordan.lee@example.test','09170000001','','2026-08-18','2026-08-18',1,'',1),(2,'TEN-2026-0002','Casey','Santos','casey.santos@example.test','09170000002','','2026-08-18','2026-08-18',1,'',2);
/*!40000 ALTER TABLE `tenants_tenant` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `violations_dormitoryrule`
--

DROP TABLE IF EXISTS `violations_dormitoryrule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `violations_dormitoryrule` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `code` varchar(20) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `title` varchar(160) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `category` varchar(80) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `description` longtext COLLATE utf8mb4_0900_as_cs NOT NULL,
  `severity` varchar(20) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `violations_dormitoryrule`
--

LOCK TABLES `violations_dormitoryrule` WRITE;
/*!40000 ALTER TABLE `violations_dormitoryrule` DISABLE KEYS */;
INSERT INTO `violations_dormitoryrule` VALUES (1,'DR-001','Quiet hours','Conduct','Keep noise to a minimum from 10:00 PM to 7:00 AM.','medium',1,'2026-08-18 10:50:37.033000'),(2,'DR-002','No alcohol containers','Safety','Alcoholic drinks and their containers are prohibited in residence areas.','high',1,'2026-08-18 10:50:37.045000'),(3,'DR-003','Fire safety','Safety','Open flames, smoking, and tampering with fire equipment are prohibited.','critical',1,'2026-08-18 10:50:37.057000'),(4,'DR-004','Guest registration','Security','All visitors must be registered and follow guest hours.','medium',1,'2026-08-18 10:50:37.068000');
/*!40000 ALTER TABLE `violations_dormitoryrule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `violations_violation`
--

DROP TABLE IF EXISTS `violations_violation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `violations_violation` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `reference` varchar(20) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `description` longtext COLLATE utf8mb4_0900_as_cs NOT NULL,
  `action_taken` varchar(255) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `evidence` varchar(100) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `recorded_at` datetime(6) NOT NULL,
  `incident_id` bigint DEFAULT NULL,
  `recorded_by_id` bigint NOT NULL,
  `rule_id` bigint NOT NULL,
  `tenant_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `reference` (`reference`),
  KEY `violations_violation_incident_id_956c61cf_fk_monitorin` (`incident_id`),
  KEY `violations_violation_recorded_by_id_4cc42654_fk_accounts_user_id` (`recorded_by_id`),
  KEY `violations_violation_rule_id_c2971f75_fk_violation` (`rule_id`),
  KEY `violations_violation_tenant_id_1b0d413f_fk_tenants_tenant_id` (`tenant_id`),
  KEY `violations_violation_recorded_at_f5d660c3` (`recorded_at`),
  CONSTRAINT `violations_violation_incident_id_956c61cf_fk_monitorin` FOREIGN KEY (`incident_id`) REFERENCES `monitoring_incident` (`id`),
  CONSTRAINT `violations_violation_recorded_by_id_4cc42654_fk_accounts_user_id` FOREIGN KEY (`recorded_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `violations_violation_rule_id_c2971f75_fk_violation` FOREIGN KEY (`rule_id`) REFERENCES `violations_dormitoryrule` (`id`),
  CONSTRAINT `violations_violation_tenant_id_1b0d413f_fk_tenants_tenant_id` FOREIGN KEY (`tenant_id`) REFERENCES `tenants_tenant` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `violations_violation`
--

LOCK TABLES `violations_violation` WRITE;
/*!40000 ALTER TABLE `violations_violation` DISABLE KEYS */;
INSERT INTO `violations_violation` VALUES (1,'VIO-2026-0001','Verified repeat noise report for demonstration.','Manager counselling','','2026-08-18 10:50:37.280000',1,1,1,1);
/*!40000 ALTER TABLE `violations_violation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `violations_warning`
--

DROP TABLE IF EXISTS `violations_warning`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `violations_warning` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `reference` varchar(20) COLLATE utf8mb4_0900_as_cs NOT NULL,
  `message` longtext COLLATE utf8mb4_0900_as_cs NOT NULL,
  `issued_at` datetime(6) NOT NULL,
  `acknowledged` tinyint(1) NOT NULL,
  `incident_id` bigint DEFAULT NULL,
  `issued_by_id` bigint NOT NULL,
  `rule_id` bigint NOT NULL,
  `tenant_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `reference` (`reference`),
  KEY `violations_warning_incident_id_f4a20742_fk_monitorin` (`incident_id`),
  KEY `violations_warning_issued_by_id_46a5cfd2_fk_accounts_user_id` (`issued_by_id`),
  KEY `violations_warning_rule_id_e2a7d935_fk_violation` (`rule_id`),
  KEY `violations_warning_tenant_id_cfca20ad_fk_tenants_tenant_id` (`tenant_id`),
  KEY `violations_warning_issued_at_51c13472` (`issued_at`),
  CONSTRAINT `violations_warning_incident_id_f4a20742_fk_monitorin` FOREIGN KEY (`incident_id`) REFERENCES `monitoring_incident` (`id`),
  CONSTRAINT `violations_warning_issued_by_id_46a5cfd2_fk_accounts_user_id` FOREIGN KEY (`issued_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `violations_warning_rule_id_e2a7d935_fk_violation` FOREIGN KEY (`rule_id`) REFERENCES `violations_dormitoryrule` (`id`),
  CONSTRAINT `violations_warning_tenant_id_cfca20ad_fk_tenants_tenant_id` FOREIGN KEY (`tenant_id`) REFERENCES `tenants_tenant` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `violations_warning`
--

LOCK TABLES `violations_warning` WRITE;
/*!40000 ALTER TABLE `violations_warning` DISABLE KEYS */;
INSERT INTO `violations_warning` VALUES (1,'WRN-2026-0001','Please observe quiet hours.','2026-08-18 10:50:37.260000',0,1,1,1,1),(2,'WRN-2026-0002','GNG','2026-08-19 09:38:08.954000',0,NULL,1,2,1);
/*!40000 ALTER TABLE `violations_warning` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'dormitory'
--

--
-- Dumping routines for database 'dormitory'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-26 17:41:50
