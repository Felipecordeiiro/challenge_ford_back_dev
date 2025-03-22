CREATE TABLE "Fact_Warranties" (
	-- FK to vehicles
	"vehicle_id" int NOT NULL UNIQUE,
	"claim_key" serial NOT NULL,
	"repair_date" date NOT NULL,
	"client_comment" text(65535),
	"tech_comment" text(65535) NOT NULL,
	-- FK to part replaced on parts
	"part_id" int NOT NULL,
	-- Result of classification model
	"classified_failured" varchar(50) NOT NULL,
	"location_id" int NOT NULL,
	"purchance_id" int NOT NULL,
	PRIMARY KEY("claim_key")
);
COMMENT ON COLUMN Fact_Warranties.vehicle_id IS 'FK to vehicles';
COMMENT ON COLUMN Fact_Warranties.part_id IS 'FK to part replaced on parts';
COMMENT ON COLUMN Fact_Warranties.classified_failured IS 'Result of classification model';


CREATE TABLE "Dim_Parts" (
	"part_id" serial NOT NULL UNIQUE,
	"part_name" varchar(255) NOT NULL,
	"last_id_purchase" int NOT NULL,
	"supplier_id" int NOT NULL,
	PRIMARY KEY("part_id")
);


CREATE TYPE "propulsion_t" AS ENUM ('eletric', 'hybrid', 'gas');

CREATE TABLE "Dim_Vehicle" (
	"vehicle_id" serial NOT NULL UNIQUE,
	"model" varchar(255) NOT NULL,
	"prod_date" date NOT NULL,
	"year" int NOT NULL,
	"propulsion" propulsion_t NOT NULL,
	PRIMARY KEY("vehicle_id")
);


CREATE TABLE "Dim_Suplier" (
	"suplier_id" serial NOT NULL UNIQUE,
	"suplier_name" varchar(50) NOT NULL,
	"supplier_cpf" varchar(20) NOT NULL,
	"location_id" int NOT NULL,
	PRIMARY KEY("suplier_id")
);


CREATE TABLE "Dim_locations" (
	"location_id" serial NOT NULL UNIQUE,
	-- market like: "north america", "european union", "east asia"
	"market" varchar(50) NOT NULL,
	"country" varchar(50) NOT NULL,
	-- state or province
	"province" varchar(50) NOT NULL,
	"city" varchar(50) NOT NULL,
	PRIMARY KEY("location_id")
);
COMMENT ON COLUMN Dim_locations.market IS 'market like: "north america", "european union", "east asia"';
COMMENT ON COLUMN Dim_locations.province IS 'state or province';

CREATE TYPE "purchance_type_t" AS ENUM ('bulk', 'warranty');

CREATE TABLE "Dim_purchances" (
	"purchance_id" serial NOT NULL UNIQUE,
	-- bulk = purchance for production
warranty = replacement
	"purchance_type" purchance_type_t NOT NULL,
	"purchance_date" date NOT NULL,
	"part_id" int NOT NULL,
	PRIMARY KEY("purchance_id")
);
COMMENT ON COLUMN Dim_purchances.purchance_type IS 'bulk = purchance for production
warranty = replacement';


ALTER TABLE "Fact_Warranties"
ADD FOREIGN KEY("part_id") REFERENCES "Dim_Parts"("part_id")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "Fact_Warranties"
ADD FOREIGN KEY("vehicle_id") REFERENCES "Dim_Vehicle"("vehicle_id")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "Dim_Suplier"
ADD FOREIGN KEY("suplier_id") REFERENCES "Dim_Parts"("supplier_id")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "Dim_Suplier"
ADD FOREIGN KEY("location_id") REFERENCES "Dim_locations"("location_id")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "Fact_Warranties"
ADD FOREIGN KEY("location_id") REFERENCES "Dim_locations"("location_id")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "Dim_Parts"
ADD FOREIGN KEY("last_id_purchase") REFERENCES "Dim_purchances"("purchance_id")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "Fact_Warranties"
ADD FOREIGN KEY("purchance_id") REFERENCES "Dim_purchances"("purchance_id")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "Dim_purchances"
ADD FOREIGN KEY("part_id") REFERENCES "Dim_Parts"("part_id")
ON UPDATE NO ACTION ON DELETE NO ACTION;