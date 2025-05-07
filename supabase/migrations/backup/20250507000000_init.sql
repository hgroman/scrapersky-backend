

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;


CREATE SCHEMA IF NOT EXISTS "public";


ALTER SCHEMA "public" OWNER TO "pg_database_owner";


COMMENT ON SCHEMA "public" IS 'standard public schema';



CREATE TYPE "public"."DomainExtractionStatusEnum" AS ENUM (
    'Queued',
    'Processing',
    'Completed',
    'Error'
);


ALTER TYPE "public"."DomainExtractionStatusEnum" OWNER TO "postgres";


CREATE TYPE "public"."SitemapAnalysisStatusEnum" AS ENUM (
    'Queued',
    'Processing',
    'Completed',
    'Error'
);


ALTER TYPE "public"."SitemapAnalysisStatusEnum" OWNER TO "postgres";


CREATE TYPE "public"."SitemapCurationStatusEnum" AS ENUM (
    'New',
    'Selected',
    'Maybe',
    'Not a Fit',
    'Archived'
);


ALTER TYPE "public"."SitemapCurationStatusEnum" OWNER TO "postgres";


CREATE TYPE "public"."app_role" AS ENUM (
    'basic',
    'admin',
    'super_admin',
    'system_admin'
);


ALTER TYPE "public"."app_role" OWNER TO "postgres";


CREATE TYPE "public"."contact_email_type_enum" AS ENUM (
    'Service',
    'Corporate',
    'Free',
    'Unknown'
);


ALTER TYPE "public"."contact_email_type_enum" OWNER TO "postgres";


CREATE TYPE "public"."feature_priority" AS ENUM (
    'urgent',
    'need_to_have',
    'nice_to_have',
    'someday'
);


ALTER TYPE "public"."feature_priority" OWNER TO "postgres";


CREATE TYPE "public"."feature_status" AS ENUM (
    'new',
    'reviewed',
    'next_round',
    'back_burner',
    'someday',
    'in_progress',
    'completed',
    'rejected'
);


ALTER TYPE "public"."feature_status" OWNER TO "postgres";


CREATE TYPE "public"."gcp_api_deep_scan_status_enum" AS ENUM (
    'Queued',
    'Processing',
    'Completed',
    'Error'
);


ALTER TYPE "public"."gcp_api_deep_scan_status_enum" OWNER TO "postgres";


CREATE TYPE "public"."pagecurationstatus" AS ENUM (
    'New',
    'Queued',
    'Processing',
    'Complete',
    'Error',
    'Skipped'
);


ALTER TYPE "public"."pagecurationstatus" OWNER TO "postgres";


CREATE TYPE "public"."pageprocessingstatus" AS ENUM (
    'Queued',
    'Processing',
    'Complete',
    'Error'
);


ALTER TYPE "public"."pageprocessingstatus" OWNER TO "postgres";


CREATE TYPE "public"."place_status_enum" AS ENUM (
    'New',
    'Selected',
    'Maybe',
    'Not a Fit',
    'Archived'
);


ALTER TYPE "public"."place_status_enum" OWNER TO "postgres";


CREATE TYPE "public"."sitemap_file_status_enum" AS ENUM (
    'Pending',
    'Processing',
    'Completed',
    'Error'
);


ALTER TYPE "public"."sitemap_file_status_enum" OWNER TO "postgres";


CREATE TYPE "public"."sitemap_import_status_enum" AS ENUM (
    'Queued',
    'Processing',
    'Completed',
    'Error'
);


ALTER TYPE "public"."sitemap_import_status_enum" OWNER TO "postgres";


CREATE TYPE "public"."task_status" AS ENUM (
    'Queued',
    'InProgress',
    'Completed',
    'Error',
    'ManualReview',
    'Cancelled',
    'Paused'
);


ALTER TYPE "public"."task_status" OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."current_user_tenant_id"() RETURNS "uuid"
    LANGUAGE "plpgsql" SECURITY DEFINER
    AS $$
    DECLARE
        tenant_id UUID;
    BEGIN
        SELECT ut.tenant_id INTO tenant_id
        FROM user_tenants ut
        WHERE ut.user_id = auth.uid();

        RETURN tenant_id;
    END;
    $$;


ALTER FUNCTION "public"."current_user_tenant_id"() OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."handle_feature_vote"() RETURNS "trigger"
    LANGUAGE "plpgsql" SECURITY DEFINER
    AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    UPDATE public.features
    SET votes = votes + 1
    WHERE id = NEW.feature_id;
  ELSIF TG_OP = 'DELETE' THEN
    UPDATE public.features
    SET votes = votes - 1
    WHERE id = OLD.feature_id;
  END IF;
  RETURN NEW;
END;
$$;


ALTER FUNCTION "public"."handle_feature_vote"() OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."handle_new_user"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$
BEGIN
  INSERT INTO public.profiles (
    id,
    tenant_id,
    name,
    email,
    role,
    role_id,
    active
  )
  VALUES (
    NEW.id,
    '550e8400-e29b-41d4-a716-446655440000',
    COALESCE(NEW.raw_user_meta_data->>'name', split_part(NEW.email, '@', 1)),
    NEW.email,
    'USER',          -- valid role name
    1,               -- USER role_id
    TRUE
  );
  RETURN NEW;
END;
$$;


ALTER FUNCTION "public"."handle_new_user"() OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."handle_updated_at"() RETURNS "trigger"
    LANGUAGE "plpgsql" SECURITY DEFINER
    AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$;


ALTER FUNCTION "public"."handle_updated_at"() OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."update_modified_column"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;


ALTER FUNCTION "public"."update_modified_column"() OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."update_updated_at_column"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;


ALTER FUNCTION "public"."update_updated_at_column"() OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."user_has_permission"("permission_name" "text") RETURNS boolean
    LANGUAGE "plpgsql" SECURITY DEFINER
    AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1
    FROM public.profiles p
    JOIN public.role_permissions rp ON p.role = rp.role
    JOIN public.permissions perm ON rp.permission_id = perm.id
    WHERE p.id = auth.uid()
    AND perm.name = permission_name
  );
END;
$$;


ALTER FUNCTION "public"."user_has_permission"("permission_name" "text") OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."validate_permission_name"() RETURNS "trigger"
    LANGUAGE "plpgsql" SECURITY DEFINER
    AS $$
        BEGIN
          IF NEW.requires_permission IS NOT NULL THEN
            IF NEW.tenant_id IS NULL THEN
              -- For global sidebar features, check global permissions
              IF NOT EXISTS (SELECT 1 FROM permissions
                            WHERE name = NEW.requires_permission) THEN
                RAISE EXCEPTION 'Global permission "%" does not exist', NEW.requires_permission;
              END IF;
            ELSE
              -- For tenant-specific sidebar features, check tenant permissions or global fallbacks
              IF NOT EXISTS (SELECT 1 FROM permissions
                            WHERE name = NEW.requires_permission) THEN
                RAISE EXCEPTION 'Permission "%" not found for tenant %',
                                NEW.requires_permission, NEW.tenant_id;
              END IF;
            END IF;
          END IF;
          RETURN NEW;
        END;
        $$;


ALTER FUNCTION "public"."validate_permission_name"() OWNER TO "postgres";

SET default_tablespace = '';

SET default_table_access_method = "heap";


CREATE TABLE IF NOT EXISTS "public"."alembic_version" (
    "version_num" character varying(32) NOT NULL
);


ALTER TABLE "public"."alembic_version" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."batch_jobs" (
    "id_uuid" "uuid" NOT NULL,
    "created_at" timestamp without time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp without time zone DEFAULT "now"() NOT NULL,
    "tenant_id" "uuid" NOT NULL,
    "processor_type" character varying NOT NULL,
    "status" character varying DEFAULT 'pending'::character varying NOT NULL,
    "created_by" "uuid",
    "total_domains" integer DEFAULT 0,
    "completed_domains" integer DEFAULT 0,
    "failed_domains" integer DEFAULT 0,
    "progress" double precision DEFAULT '0'::double precision,
    "batch_metadata" "jsonb",
    "options" "jsonb",
    "start_time" timestamp without time zone,
    "end_time" timestamp without time zone,
    "processing_time" double precision,
    "error" character varying,
    "id" integer NOT NULL,
    "batch_id_string" character varying,
    "batch_id" "uuid",
    "batch_id_original" character varying
);


ALTER TABLE "public"."batch_jobs" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."batch_jobs_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE "public"."batch_jobs_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."batch_jobs_id_seq" OWNED BY "public"."batch_jobs"."id";



CREATE TABLE IF NOT EXISTS "public"."contacts" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "domain_id" "uuid" NOT NULL,
    "page_id" "uuid" NOT NULL,
    "email" "text" NOT NULL,
    "email_type" "public"."contact_email_type_enum",
    "has_gmail" boolean DEFAULT false,
    "context" "text",
    "source_url" "text",
    "source_job_id" "uuid",
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL
);


ALTER TABLE "public"."contacts" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."domains" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "tenant_id" "uuid" NOT NULL,
    "domain" character varying NOT NULL,
    "lead_source" "text",
    "is_active" boolean DEFAULT true,
    "status" character varying DEFAULT 'active'::"text" NOT NULL,
    "local_business_scraped_status" "text",
    "local_business_scraped_at" timestamp with time zone,
    "agency_sitemap_analysis_done" "text",
    "agency_sitemap_analysis_done_at" timestamp with time zone,
    "agency_wordpress_details" "text",
    "agency_wordpress_details_at" timestamp with time zone,
    "agency_copyright_status" "text",
    "agency_copyright_status_at" timestamp with time zone,
    "agency_ad_performance_status" "text",
    "agency_ad_performance_at" timestamp with time zone,
    "content_scrape_status" "public"."task_status" DEFAULT 'Queued'::"public"."task_status",
    "content_scrape_at" timestamp with time zone,
    "content_scrape_error" "text",
    "page_scrape_status" "public"."task_status" DEFAULT 'Queued'::"public"."task_status",
    "page_scrape_at" timestamp with time zone,
    "page_scrape_error" "text",
    "sitemap_monitor_status" "public"."task_status" DEFAULT 'Queued'::"public"."task_status",
    "sitemap_monitor_at" timestamp with time zone,
    "sitemap_monitor_error" "text",
    "has_ssl" boolean,
    "ssl_expiry_date" timestamp with time zone,
    "security_headers" "jsonb",
    "ssl_issuer" "text",
    "ssl_version" "text",
    "server_type" "text",
    "ip_address" "text",
    "hosting_provider" "text",
    "country_code" "text",
    "server_response_time" integer,
    "dns_records" "jsonb",
    "hosting_location" "text",
    "cdn_provider" "text",
    "last_modified" timestamp with time zone,
    "robots_txt" "text",
    "has_sitemap" boolean,
    "page_count" integer,
    "content_language" "text"[],
    "feed_urls" "jsonb",
    "average_page_size" integer,
    "total_images_count" integer,
    "crawler_hints" "jsonb",
    "business_category" "text",
    "estimated_traffic" "jsonb",
    "has_ecommerce" boolean,
    "primary_language" "text",
    "business_hours" "jsonb",
    "payment_methods" "text"[],
    "business_type" "text",
    "industry_vertical" "text",
    "competitor_group" "text",
    "market_segment" "text",
    "last_error" "text",
    "error_count" integer DEFAULT 0,
    "last_successful_scan" timestamp with time zone,
    "average_response_time" integer,
    "uptime_percentage" numeric(5,2),
    "error_history" "jsonb",
    "performance_metrics" "jsonb",
    "monitoring_status" "text",
    "alert_threshold" "jsonb",
    "sitemap_url" "text",
    "tech_stack" "jsonb",
    "first_scan" timestamp with time zone DEFAULT "now"() NOT NULL,
    "last_scan" timestamp with time zone DEFAULT "now"() NOT NULL,
    "title" "text",
    "description" "text",
    "favicon_url" "text",
    "logo_url" "text",
    "copyright_year" "text",
    "language" "text",
    "has_cookie_notice" boolean,
    "has_privacy_policy" boolean,
    "google_analytics_id" "text",
    "google_tag_manager_id" "text",
    "is_wordpress" boolean,
    "wordpress_version" "text",
    "wordpress_theme" "text",
    "has_elementor" boolean,
    "elementor_version" "text",
    "has_divi" boolean,
    "has_woocommerce" boolean,
    "has_contact_form7" boolean,
    "has_yoast_seo" boolean,
    "has_wpforms" boolean,
    "phone_numbers" "text"[],
    "email_addresses" "text"[],
    "physical_addresses" "text"[],
    "facebook_url" "text",
    "twitter_url" "text",
    "linkedin_url" "text",
    "instagram_url" "text",
    "youtube_url" "text",
    "meta_json" "jsonb" DEFAULT '{}'::"jsonb",
    "created_at" timestamp without time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp without time zone DEFAULT "now"() NOT NULL,
    "created_by" "uuid",
    "domain_metadata" "jsonb",
    "notes" "text",
    "batch_id" character varying,
    "sitemap_urls" integer DEFAULT 0,
    "total_sitemaps" integer DEFAULT 0,
    "local_business_id" "uuid",
    "sitemap_curation_status" "public"."SitemapCurationStatusEnum" DEFAULT 'New'::"public"."SitemapCurationStatusEnum",
    "sitemap_analysis_status" "public"."SitemapAnalysisStatusEnum",
    "sitemap_analysis_error" "text"
);


ALTER TABLE "public"."domains" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."feature_flags" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "name" "text" NOT NULL,
    "description" "text",
    "default_enabled" boolean DEFAULT false,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."feature_flags" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."feature_votes" (
    "feature_id" "uuid" NOT NULL,
    "user_id" "uuid" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL
);


ALTER TABLE "public"."feature_votes" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."features" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "title" "text" NOT NULL,
    "description" "text",
    "priority" "text" NOT NULL,
    "status" "text" DEFAULT 'new'::"text" NOT NULL,
    "requested_by" "uuid",
    "reviewed_by" "uuid",
    "votes" integer DEFAULT 0 NOT NULL,
    "page_path" "text",
    "page_tab" "text",
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL
);


ALTER TABLE "public"."features" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."jobs" (
    "id" integer NOT NULL,
    "job_id" "uuid" NOT NULL,
    "tenant_id" character varying(255) NOT NULL,
    "status" character varying(50) NOT NULL,
    "job_type" character varying(50) NOT NULL,
    "created_at" timestamp without time zone DEFAULT "now"() NOT NULL,
    "started_at" timestamp with time zone,
    "completed_at" timestamp with time zone,
    "progress" double precision DEFAULT '0'::double precision,
    "error" character varying,
    "result" "jsonb",
    "metadata" "jsonb",
    "created_by" "uuid",
    "domain_id" "uuid",
    "result_data" "jsonb",
    "job_metadata" "jsonb",
    "updated_at" timestamp without time zone DEFAULT "now"() NOT NULL,
    "tenant_id_uuid" "uuid",
    "id_uuid" "uuid",
    "batch_id" character varying,
    "batch_id_string" character varying
);


ALTER TABLE "public"."jobs" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."jobs_backup" (
    "id" integer,
    "job_id" character varying(255),
    "tenant_id" character varying(255),
    "status" character varying(50),
    "job_type" character varying(50),
    "created_at" timestamp without time zone,
    "started_at" timestamp with time zone,
    "completed_at" timestamp with time zone,
    "progress" double precision,
    "error" character varying,
    "result" "jsonb",
    "metadata" "jsonb",
    "created_by" "uuid",
    "domain_id" "uuid",
    "result_data" "jsonb",
    "job_metadata" "jsonb",
    "updated_at" timestamp without time zone,
    "tenant_id_uuid" "uuid",
    "id_uuid" "uuid",
    "batch_id" character varying
);


ALTER TABLE "public"."jobs_backup" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."jobs_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE "public"."jobs_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."jobs_id_seq" OWNED BY "public"."jobs"."id";



CREATE TABLE IF NOT EXISTS "public"."local_businesses" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "tenant_id" "uuid" NOT NULL,
    "lead_source" "text",
    "business_name" "text",
    "full_address" "text",
    "street_address" "text",
    "city" "text",
    "state" "text",
    "zip" "text",
    "country" "text",
    "phone" "text",
    "main_category" "text",
    "extra_categories" "text"[],
    "rating" numeric,
    "reviews_count" integer,
    "price_text" "text",
    "website_url" "text",
    "business_verified" boolean,
    "monday_hours" "text",
    "tuesday_hours" "text",
    "wednesday_hours" "text",
    "thursday_hours" "text",
    "friday_hours" "text",
    "saturday_hours" "text",
    "sunday_hours" "text",
    "timezone" "text",
    "image_url" "text",
    "latitude" numeric,
    "longitude" numeric,
    "food_featured" boolean,
    "hotel_featured" boolean,
    "service_options" "text"[],
    "highlights" "text"[],
    "popular_for" "text"[],
    "accessibility" "text"[],
    "offerings" "text"[],
    "dining_options" "text"[],
    "amenities" "text"[],
    "atmosphere" "text"[],
    "crowd" "text"[],
    "planning" "text"[],
    "payments" "text"[],
    "children" "text"[],
    "parking" "text"[],
    "pets" "text"[],
    "additional_json" "jsonb" DEFAULT '{}'::"jsonb",
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "place_id" "text",
    "status" "public"."place_status_enum" DEFAULT 'New'::"public"."place_status_enum",
    "domain_extraction_status" "public"."DomainExtractionStatusEnum",
    "domain_extraction_error" "text"
);


ALTER TABLE "public"."local_businesses" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."migration_logs" (
    "id" integer NOT NULL,
    "migration_name" "text" NOT NULL,
    "log_data" "jsonb" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."migration_logs" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."migration_logs_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE "public"."migration_logs_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."migration_logs_id_seq" OWNED BY "public"."migration_logs"."id";



CREATE TABLE IF NOT EXISTS "public"."pages" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "tenant_id" "uuid" NOT NULL,
    "domain_id" "uuid" NOT NULL,
    "url" "text" NOT NULL,
    "title" "text",
    "description" "text",
    "h1" "text",
    "canonical_url" "text",
    "meta_robots" "text",
    "has_schema_markup" boolean DEFAULT false,
    "schema_types" "text"[],
    "has_contact_form" boolean DEFAULT false,
    "has_comments" boolean DEFAULT false,
    "word_count" integer,
    "inbound_links" "text"[],
    "outbound_links" "text"[],
    "last_modified" timestamp with time zone,
    "last_scan" timestamp with time zone,
    "page_type" "text",
    "lead_source" "text",
    "additional_json" "jsonb" DEFAULT '{}'::"jsonb",
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"(),
    "sitemap_file_id" "uuid",
    "page_curation_status" "public"."pagecurationstatus" DEFAULT 'New'::"public"."pagecurationstatus" NOT NULL,
    "page_processing_status" "public"."pageprocessingstatus",
    "page_processing_error" "text"
);


ALTER TABLE "public"."pages" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."permissions" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "name" "text" NOT NULL,
    "description" "text",
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL
);


ALTER TABLE "public"."permissions" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."place_searches" (
    "id" "uuid" NOT NULL,
    "tenant_id" "uuid" NOT NULL,
    "user_id" "uuid",
    "location" character varying(255) NOT NULL,
    "business_type" character varying(100) NOT NULL,
    "params" "jsonb",
    "created_at" timestamp without time zone DEFAULT "now"(),
    "status" character varying(50) DEFAULT 'pending'::character varying,
    "updated_at" timestamp without time zone DEFAULT "now"()
);


ALTER TABLE "public"."place_searches" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."places_staging" (
    "id" integer NOT NULL,
    "place_id" "text" NOT NULL,
    "name" "text" NOT NULL,
    "formatted_address" "text",
    "business_type" "text",
    "latitude" double precision,
    "longitude" double precision,
    "vicinity" "text",
    "rating" double precision,
    "user_ratings_total" integer,
    "price_level" integer,
    "tenant_id" "uuid",
    "created_by" "uuid" NOT NULL,
    "search_job_id" "uuid",
    "search_query" "text",
    "search_location" "text",
    "search_time" timestamp with time zone DEFAULT "now"(),
    "status" "public"."place_status_enum" DEFAULT 'New'::"public"."place_status_enum" NOT NULL,
    "notes" "text",
    "priority" integer DEFAULT 0,
    "tags" "text"[],
    "revisit_date" "date",
    "processed" boolean DEFAULT false,
    "processed_time" timestamp with time zone,
    "raw_data" "jsonb",
    "user_id" "uuid",
    "user_name" "text",
    "updated_by" "text",
    "updated_at" timestamp with time zone DEFAULT "now"(),
    "deep_scan_error" "text",
    "deep_scan_status" "public"."gcp_api_deep_scan_status_enum"
);


ALTER TABLE "public"."places_staging" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."places_staging_backup" (
    "id" integer,
    "place_id" "text",
    "name" "text",
    "formatted_address" "text",
    "business_type" "text",
    "latitude" double precision,
    "longitude" double precision,
    "vicinity" "text",
    "rating" double precision,
    "user_ratings_total" integer,
    "price_level" integer,
    "tenant_id" "text",
    "created_by" "text",
    "search_job_id" "text",
    "search_query" "text",
    "search_location" "text",
    "search_time" timestamp with time zone,
    "status" "text",
    "notes" "text",
    "priority" integer,
    "tags" "text"[],
    "revisit_date" "date",
    "processed" boolean,
    "processed_time" timestamp with time zone,
    "raw_data" "jsonb",
    "user_id" "text",
    "user_name" "text",
    "updated_by" "text",
    "updated_at" timestamp with time zone
);


ALTER TABLE "public"."places_staging_backup" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."places_staging_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE "public"."places_staging_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."places_staging_id_seq" OWNED BY "public"."places_staging"."id";



CREATE TABLE IF NOT EXISTS "public"."profiles" (
    "id" "uuid" NOT NULL,
    "tenant_id" "uuid" DEFAULT '550e8400-e29b-41d4-a716-446655440000'::"uuid" NOT NULL,
    "name" "text",
    "email" "text",
    "avatar_url" "text",
    "bio" "text",
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"(),
    "active" boolean DEFAULT false,
    "role" "text" DEFAULT 'USER'::"text",
    "role_id" integer,
    CONSTRAINT "profiles_role_check" CHECK (("role" = ANY (ARRAY['USER'::"text", 'ADMIN'::"text", 'SUPER_ADMIN'::"text", 'GLOBAL_ADMIN'::"text"])))
);


ALTER TABLE "public"."profiles" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."role_permissions" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "role_id" integer NOT NULL,
    "permission_id" "uuid" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL
);


ALTER TABLE "public"."role_permissions" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."roles" (
    "id" integer NOT NULL,
    "name" "text" NOT NULL,
    "description" "text",
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "tenant_id" "uuid" NOT NULL
);


ALTER TABLE "public"."roles" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."roles_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE "public"."roles_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."roles_id_seq" OWNED BY "public"."roles"."id";



CREATE TABLE IF NOT EXISTS "public"."sidebar_features" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "feature_id" "uuid",
    "sidebar_name" "text" NOT NULL,
    "url_path" "text" NOT NULL,
    "icon" "text",
    "display_order" integer,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"(),
    "requires_permission" "text",
    "requires_feature" "uuid",
    "tenant_id" "uuid",
    "group_name" "text",
    "minimum_role_id" integer DEFAULT 1
);


ALTER TABLE "public"."sidebar_features" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."sitemap_files" (
    "id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "tenant_id" "uuid" DEFAULT '550e8400-e29b-41d4-a716-446655440000'::"uuid",
    "domain_id" "uuid" NOT NULL,
    "url" "text" NOT NULL,
    "sitemap_type" "text" NOT NULL,
    "discovery_method" "text",
    "page_count" integer,
    "size_bytes" integer,
    "response_time_ms" integer,
    "status" "text" DEFAULT 'new'::"text" NOT NULL,
    "priority" integer DEFAULT 5,
    "status_code" integer,
    "error_message" "text",
    "last_modified" timestamp with time zone,
    "is_gzipped" boolean,
    "has_lastmod" boolean,
    "has_priority" boolean,
    "has_changefreq" boolean,
    "generator" "text",
    "lead_source" "text",
    "user_id" "uuid",
    "user_name" "text",
    "notes" "text",
    "tags" "text"[],
    "is_active" boolean DEFAULT true,
    "process_after" timestamp with time zone,
    "last_processed_at" timestamp with time zone,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "created_by" "uuid",
    "updated_at" timestamp with time zone DEFAULT "now"(),
    "updated_by" "uuid",
    "job_id" "uuid",
    "url_count" integer DEFAULT 0,
    "deep_scrape_curation_status" "public"."SitemapCurationStatusEnum" DEFAULT 'New'::"public"."SitemapCurationStatusEnum",
    "sitemap_import_error" "text",
    "sitemap_import_status" "public"."sitemap_import_status_enum"
);


ALTER TABLE "public"."sitemap_files" OWNER TO "postgres";


COMMENT ON COLUMN "public"."sitemap_files"."url_count" IS 'Number of URLs found in this sitemap file';



COMMENT ON COLUMN "public"."sitemap_files"."sitemap_import_status" IS 'Status of the deep scrape process, using the deep_scan_status_enum type.';



CREATE TABLE IF NOT EXISTS "public"."sitemap_files_backup" (
    "id" "uuid",
    "tenant_id" "uuid",
    "domain_id" "uuid",
    "url" "text",
    "sitemap_type" "text",
    "discovery_method" "text",
    "page_count" integer,
    "size_bytes" integer,
    "response_time_ms" integer,
    "status" "text",
    "priority" integer,
    "status_code" integer,
    "error_message" "text",
    "last_modified" timestamp with time zone,
    "is_gzipped" boolean,
    "has_lastmod" boolean,
    "has_priority" boolean,
    "has_changefreq" boolean,
    "generator" "text",
    "lead_source" "text",
    "user_id" "uuid",
    "user_name" "text",
    "notes" "text",
    "tags" "text"[],
    "is_active" boolean,
    "process_after" timestamp with time zone,
    "last_processed_at" timestamp with time zone,
    "created_at" timestamp with time zone,
    "created_by" "uuid",
    "updated_at" timestamp with time zone,
    "updated_by" "uuid",
    "job_id" "text",
    "url_count" integer
);


ALTER TABLE "public"."sitemap_files_backup" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."sitemap_urls" (
    "id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "tenant_id" "uuid" DEFAULT '550e8400-e29b-41d4-a716-446655440000'::"uuid",
    "domain_id" "uuid" NOT NULL,
    "sitemap_id" "uuid" NOT NULL,
    "url" "text" NOT NULL,
    "loc_text" "text" NOT NULL,
    "page_type" "text",
    "status" "text" DEFAULT 'new'::"text" NOT NULL,
    "priority" integer DEFAULT 5,
    "status_code" integer,
    "error_message" "text",
    "lastmod" timestamp with time zone,
    "changefreq" "text",
    "priority_value" numeric(3,2),
    "image_count" integer,
    "video_count" integer,
    "news_count" integer,
    "size_bytes" integer,
    "lead_source" "text",
    "user_id" "uuid",
    "user_name" "text",
    "notes" "text",
    "tags" "text"[],
    "is_active" boolean DEFAULT true,
    "process_after" timestamp with time zone,
    "discovered_at" timestamp with time zone DEFAULT "now"(),
    "last_checked_at" timestamp with time zone,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "created_by" "uuid",
    "updated_at" timestamp with time zone DEFAULT "now"(),
    "updated_by" "uuid"
);


ALTER TABLE "public"."sitemap_urls" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."task_analytics" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "tenant_id" "uuid" NOT NULL,
    "task_id" "uuid" NOT NULL,
    "time_in_status" integer,
    "status" "text" NOT NULL,
    "completion_time" integer,
    "agent_id" "uuid",
    "performance_score" numeric,
    "meta_json" "jsonb" DEFAULT '{}'::"jsonb",
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL
);


ALTER TABLE "public"."task_analytics" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."task_history" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "tenant_id" "uuid" NOT NULL,
    "task_id" "uuid" NOT NULL,
    "changed_by" "uuid" NOT NULL,
    "previous_status" "text",
    "new_status" "text" NOT NULL,
    "previous_assigned_to" "uuid",
    "new_assigned_to" "uuid",
    "change_type" "text" NOT NULL,
    "notes" "text",
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL
);


ALTER TABLE "public"."task_history" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."tasks" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "tenant_id" "uuid" NOT NULL,
    "name" "text" NOT NULL,
    "description" "text",
    "status" "text" DEFAULT 'pending'::"text" NOT NULL,
    "priority" "text" DEFAULT 'medium'::"text" NOT NULL,
    "assigned_to" "uuid",
    "assigned_by" "uuid",
    "due_date" timestamp with time zone,
    "completed_at" timestamp with time zone,
    "task_type" "text" NOT NULL,
    "domain_id" "uuid",
    "page_id" "uuid",
    "meta_json" "jsonb" DEFAULT '{}'::"jsonb",
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."tasks" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."tenant_features" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "tenant_id" "uuid" NOT NULL,
    "feature_id" "uuid" NOT NULL,
    "is_enabled" boolean DEFAULT false,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."tenant_features" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."tenants" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "name" "text" NOT NULL,
    "description" "text",
    "is_active" boolean DEFAULT true NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL
);


ALTER TABLE "public"."tenants" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."user_roles" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "user_id" "uuid" NOT NULL,
    "role_id" integer NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "tenant_id" "uuid",
    "updated_at" timestamp with time zone
);


ALTER TABLE "public"."user_roles" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."user_tenants" (
    "user_id" "uuid" NOT NULL,
    "tenant_id" "uuid" NOT NULL,
    "role_id" integer,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL
);


ALTER TABLE "public"."user_tenants" OWNER TO "postgres";


ALTER TABLE ONLY "public"."batch_jobs" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."batch_jobs_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."jobs" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."jobs_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."migration_logs" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."migration_logs_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."places_staging" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."places_staging_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."roles" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."roles_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."alembic_version"
    ADD CONSTRAINT "alembic_version_pkc" PRIMARY KEY ("version_num");



ALTER TABLE ONLY "public"."batch_jobs"
    ADD CONSTRAINT "batch_jobs_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."contacts"
    ADD CONSTRAINT "contacts_domain_id_email_key" UNIQUE ("domain_id", "email");



ALTER TABLE ONLY "public"."contacts"
    ADD CONSTRAINT "contacts_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."domains"
    ADD CONSTRAINT "domains_domain_key" UNIQUE ("domain");



ALTER TABLE ONLY "public"."domains"
    ADD CONSTRAINT "domains_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."feature_flags"
    ADD CONSTRAINT "feature_flags_name_key" UNIQUE ("name");



ALTER TABLE ONLY "public"."feature_flags"
    ADD CONSTRAINT "feature_flags_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."feature_votes"
    ADD CONSTRAINT "feature_votes_pkey" PRIMARY KEY ("feature_id", "user_id");



ALTER TABLE ONLY "public"."features"
    ADD CONSTRAINT "features_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."jobs"
    ADD CONSTRAINT "jobs_job_id_key" UNIQUE ("job_id");



ALTER TABLE ONLY "public"."jobs"
    ADD CONSTRAINT "jobs_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."local_businesses"
    ADD CONSTRAINT "local_businesses_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."local_businesses"
    ADD CONSTRAINT "local_businesses_place_id_key" UNIQUE ("place_id");



ALTER TABLE ONLY "public"."migration_logs"
    ADD CONSTRAINT "migration_logs_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."pages"
    ADD CONSTRAINT "pages_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."permissions"
    ADD CONSTRAINT "permissions_name_key" UNIQUE ("name");



ALTER TABLE ONLY "public"."permissions"
    ADD CONSTRAINT "permissions_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."place_searches"
    ADD CONSTRAINT "place_searches_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."places_staging"
    ADD CONSTRAINT "places_staging_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."places_staging"
    ADD CONSTRAINT "places_staging_place_id_key" UNIQUE ("place_id");



ALTER TABLE ONLY "public"."profiles"
    ADD CONSTRAINT "profiles_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."role_permissions"
    ADD CONSTRAINT "role_permissions_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."role_permissions"
    ADD CONSTRAINT "role_permissions_role_id_permission_id_key" UNIQUE ("role_id", "permission_id");



ALTER TABLE ONLY "public"."roles"
    ADD CONSTRAINT "roles_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."sidebar_features"
    ADD CONSTRAINT "sidebar_features_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."sitemap_files"
    ADD CONSTRAINT "sitemap_files_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."sitemap_urls"
    ADD CONSTRAINT "sitemap_urls_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."task_analytics"
    ADD CONSTRAINT "task_analytics_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."task_history"
    ADD CONSTRAINT "task_history_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."tasks"
    ADD CONSTRAINT "tasks_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."tenant_features"
    ADD CONSTRAINT "tenant_features_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."tenant_features"
    ADD CONSTRAINT "tenant_features_tenant_id_feature_id_key" UNIQUE ("tenant_id", "feature_id");



ALTER TABLE ONLY "public"."tenants"
    ADD CONSTRAINT "tenants_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."permissions"
    ADD CONSTRAINT "unique_permission_name" UNIQUE ("name");



ALTER TABLE ONLY "public"."domains"
    ADD CONSTRAINT "uq_domains_domain" UNIQUE ("domain");



ALTER TABLE ONLY "public"."roles"
    ADD CONSTRAINT "uq_role_name_tenant" UNIQUE ("name", "tenant_id");



ALTER TABLE ONLY "public"."user_roles"
    ADD CONSTRAINT "user_roles_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."user_roles"
    ADD CONSTRAINT "user_roles_user_id_role_id_key" UNIQUE ("user_id", "role_id");



ALTER TABLE ONLY "public"."user_tenants"
    ADD CONSTRAINT "user_tenants_pkey" PRIMARY KEY ("user_id", "tenant_id");



CREATE INDEX "idx_contacts_domain_email" ON "public"."contacts" USING "btree" ("domain_id", "email");



CREATE INDEX "idx_contacts_page_id" ON "public"."contacts" USING "btree" ("page_id");



CREATE INDEX "idx_domains_business_category" ON "public"."domains" USING "btree" ("business_category");



CREATE INDEX "idx_domains_business_type" ON "public"."domains" USING "btree" ("business_type");



CREATE INDEX "idx_domains_content_scrape_status" ON "public"."domains" USING "btree" ("content_scrape_status");



CREATE INDEX "idx_domains_country_code" ON "public"."domains" USING "btree" ("country_code");



CREATE INDEX "idx_domains_domain" ON "public"."domains" USING "btree" ("domain");



CREATE INDEX "idx_domains_has_ssl" ON "public"."domains" USING "btree" ("has_ssl");



CREATE INDEX "idx_domains_hosting_provider" ON "public"."domains" USING "btree" ("hosting_provider");



CREATE INDEX "idx_domains_industry_vertical" ON "public"."domains" USING "btree" ("industry_vertical");



CREATE INDEX "idx_domains_local_business_id" ON "public"."domains" USING "btree" ("local_business_id");



CREATE INDEX "idx_domains_page_scrape_status" ON "public"."domains" USING "btree" ("page_scrape_status");



CREATE INDEX "idx_domains_sitemap_analysis_status" ON "public"."domains" USING "btree" ("sitemap_analysis_status");



CREATE INDEX "idx_domains_sitemap_curation_status" ON "public"."domains" USING "btree" ("sitemap_curation_status");



CREATE INDEX "idx_domains_sitemap_monitor_status" ON "public"."domains" USING "btree" ("sitemap_monitor_status");



CREATE INDEX "idx_domains_status" ON "public"."domains" USING "btree" ("status");



CREATE INDEX "idx_domains_tenant_id" ON "public"."domains" USING "btree" ("tenant_id");



CREATE INDEX "idx_jobs_tenant_id" ON "public"."jobs" USING "btree" ("tenant_id");



CREATE INDEX "idx_local_businesses_domain_extraction_status" ON "public"."local_businesses" USING "btree" ("domain_extraction_status");



CREATE INDEX "idx_local_businesses_status" ON "public"."local_businesses" USING "btree" ("status");



CREATE INDEX "idx_local_businesses_tenant_id" ON "public"."local_businesses" USING "btree" ("tenant_id");



CREATE INDEX "idx_pages_domain_id" ON "public"."pages" USING "btree" ("domain_id");



CREATE INDEX "idx_pages_page_curation_status" ON "public"."pages" USING "btree" ("page_curation_status");



CREATE INDEX "idx_pages_page_processing_status" ON "public"."pages" USING "btree" ("page_processing_status");



CREATE INDEX "idx_pages_sitemap_file_id" ON "public"."pages" USING "btree" ("sitemap_file_id");



CREATE INDEX "idx_places_staging_status" ON "public"."places_staging" USING "btree" ("status");



CREATE INDEX "idx_places_staging_tenant" ON "public"."places_staging" USING "btree" ("tenant_id");



CREATE INDEX "idx_profiles_tenant_id" ON "public"."profiles" USING "btree" ("tenant_id");



CREATE INDEX "idx_sitemap_files_deep_scrape_process_status" ON "public"."sitemap_files" USING "btree" ("sitemap_import_status");



CREATE INDEX "idx_sitemap_files_status" ON "public"."sitemap_files" USING "btree" ("status");



CREATE INDEX "idx_sitemap_files_tenant_domain" ON "public"."sitemap_files" USING "btree" ("tenant_id", "domain_id");



CREATE INDEX "idx_sitemap_urls_sitemap_id" ON "public"."sitemap_urls" USING "btree" ("sitemap_id");



CREATE INDEX "idx_sitemap_urls_status" ON "public"."sitemap_urls" USING "btree" ("status");



CREATE INDEX "idx_sitemap_urls_tenant_domain" ON "public"."sitemap_urls" USING "btree" ("tenant_id", "domain_id");



CREATE INDEX "idx_task_analytics_task_id" ON "public"."task_analytics" USING "btree" ("task_id");



CREATE INDEX "idx_task_analytics_tenant_id" ON "public"."task_analytics" USING "btree" ("tenant_id");



CREATE INDEX "idx_task_history_task_id" ON "public"."task_history" USING "btree" ("task_id");



CREATE INDEX "idx_task_history_tenant_id" ON "public"."task_history" USING "btree" ("tenant_id");



CREATE INDEX "idx_tasks_domain_id" ON "public"."tasks" USING "btree" ("domain_id");



CREATE INDEX "idx_tasks_page_id" ON "public"."tasks" USING "btree" ("page_id");



CREATE INDEX "idx_user_roles_user_id" ON "public"."user_roles" USING "btree" ("user_id");



CREATE INDEX "ix_batch_jobs_tenant_id" ON "public"."batch_jobs" USING "btree" ("tenant_id");



CREATE INDEX "ix_domains_batch_id" ON "public"."domains" USING "btree" ("batch_id");



CREATE INDEX "ix_domains_domain" ON "public"."domains" USING "btree" ("domain");



CREATE INDEX "ix_domains_tenant_id" ON "public"."domains" USING "btree" ("tenant_id");



CREATE INDEX "ix_jobs_batch_id" ON "public"."jobs" USING "btree" ("batch_id");



CREATE INDEX "ix_jobs_tenant_id_uuid" ON "public"."jobs" USING "btree" ("tenant_id_uuid");



CREATE INDEX "ix_local_businesses_place_id" ON "public"."local_businesses" USING "btree" ("place_id");



CREATE INDEX "ix_places_staging_status" ON "public"."places_staging" USING "btree" ("status");



CREATE INDEX "ix_user_roles_tenant_id" ON "public"."user_roles" USING "btree" ("tenant_id");



CREATE OR REPLACE TRIGGER "on_feature_vote" AFTER INSERT OR DELETE ON "public"."feature_votes" FOR EACH ROW EXECUTE FUNCTION "public"."handle_feature_vote"();



CREATE OR REPLACE TRIGGER "trg_validate_permission" BEFORE INSERT OR UPDATE ON "public"."sidebar_features" FOR EACH ROW EXECUTE FUNCTION "public"."validate_permission_name"();



CREATE OR REPLACE TRIGGER "update_features_updated_at" BEFORE UPDATE ON "public"."features" FOR EACH ROW EXECUTE FUNCTION "public"."update_updated_at_column"();



CREATE OR REPLACE TRIGGER "update_pages_updated_at" BEFORE UPDATE ON "public"."pages" FOR EACH ROW EXECUTE FUNCTION "public"."update_updated_at_column"();



CREATE OR REPLACE TRIGGER "update_places_staging_modtime" BEFORE UPDATE ON "public"."places_staging" FOR EACH ROW EXECUTE FUNCTION "public"."update_modified_column"();



CREATE OR REPLACE TRIGGER "update_tasks_updated_at" BEFORE UPDATE ON "public"."tasks" FOR EACH ROW EXECUTE FUNCTION "public"."update_updated_at_column"();



ALTER TABLE ONLY "public"."contacts"
    ADD CONSTRAINT "contacts_domain_id_fkey" FOREIGN KEY ("domain_id") REFERENCES "public"."domains"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."contacts"
    ADD CONSTRAINT "contacts_page_id_fkey" FOREIGN KEY ("page_id") REFERENCES "public"."pages"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."contacts"
    ADD CONSTRAINT "contacts_source_job_id_fkey" FOREIGN KEY ("source_job_id") REFERENCES "public"."jobs"("job_id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."feature_votes"
    ADD CONSTRAINT "feature_votes_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."features"
    ADD CONSTRAINT "features_requested_by_fkey" FOREIGN KEY ("requested_by") REFERENCES "auth"."users"("id");



ALTER TABLE ONLY "public"."features"
    ADD CONSTRAINT "features_reviewed_by_fkey" FOREIGN KEY ("reviewed_by") REFERENCES "auth"."users"("id");



ALTER TABLE ONLY "public"."domains"
    ADD CONSTRAINT "fk_domains_local_business" FOREIGN KEY ("local_business_id") REFERENCES "public"."local_businesses"("id") ON UPDATE CASCADE ON DELETE SET NULL;



ALTER TABLE ONLY "public"."jobs"
    ADD CONSTRAINT "fk_jobs_domain_id" FOREIGN KEY ("domain_id") REFERENCES "public"."domains"("id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."pages"
    ADD CONSTRAINT "fk_pages_sitemap_file_id" FOREIGN KEY ("sitemap_file_id") REFERENCES "public"."sitemap_files"("id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."profiles"
    ADD CONSTRAINT "fk_profiles_tenant" FOREIGN KEY ("tenant_id") REFERENCES "public"."tenants"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."roles"
    ADD CONSTRAINT "fk_roles_tenant_id_tenants" FOREIGN KEY ("tenant_id") REFERENCES "public"."tenants"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."user_roles"
    ADD CONSTRAINT "fk_user_roles_profile" FOREIGN KEY ("user_id") REFERENCES "public"."profiles"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."user_roles"
    ADD CONSTRAINT "fk_user_roles_tenant_id" FOREIGN KEY ("tenant_id") REFERENCES "public"."tenants"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."pages"
    ADD CONSTRAINT "pages_domain_id_fkey" FOREIGN KEY ("domain_id") REFERENCES "public"."domains"("id");



ALTER TABLE ONLY "public"."profiles"
    ADD CONSTRAINT "profiles_id_fkey" FOREIGN KEY ("id") REFERENCES "auth"."users"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."profiles"
    ADD CONSTRAINT "profiles_role_id_fkey" FOREIGN KEY ("role_id") REFERENCES "public"."roles"("id");



ALTER TABLE ONLY "public"."role_permissions"
    ADD CONSTRAINT "role_permissions_permission_id_fkey" FOREIGN KEY ("permission_id") REFERENCES "public"."permissions"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."role_permissions"
    ADD CONSTRAINT "role_permissions_role_id_fkey" FOREIGN KEY ("role_id") REFERENCES "public"."roles"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."sidebar_features"
    ADD CONSTRAINT "sidebar_features_feature_id_fkey" FOREIGN KEY ("feature_id") REFERENCES "public"."feature_flags"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."sidebar_features"
    ADD CONSTRAINT "sidebar_features_requires_feature_fkey" FOREIGN KEY ("requires_feature") REFERENCES "public"."feature_flags"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."sitemap_files"
    ADD CONSTRAINT "sitemap_files_created_by_fkey" FOREIGN KEY ("created_by") REFERENCES "auth"."users"("id");



ALTER TABLE ONLY "public"."sitemap_files"
    ADD CONSTRAINT "sitemap_files_domain_id_fkey" FOREIGN KEY ("domain_id") REFERENCES "public"."domains"("id");



ALTER TABLE ONLY "public"."sitemap_files"
    ADD CONSTRAINT "sitemap_files_updated_by_fkey" FOREIGN KEY ("updated_by") REFERENCES "auth"."users"("id");



ALTER TABLE ONLY "public"."sitemap_files"
    ADD CONSTRAINT "sitemap_files_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id");



ALTER TABLE ONLY "public"."sitemap_urls"
    ADD CONSTRAINT "sitemap_urls_created_by_fkey" FOREIGN KEY ("created_by") REFERENCES "auth"."users"("id");



ALTER TABLE ONLY "public"."sitemap_urls"
    ADD CONSTRAINT "sitemap_urls_domain_id_fkey" FOREIGN KEY ("domain_id") REFERENCES "public"."domains"("id");



ALTER TABLE ONLY "public"."sitemap_urls"
    ADD CONSTRAINT "sitemap_urls_sitemap_id_fkey" FOREIGN KEY ("sitemap_id") REFERENCES "public"."sitemap_files"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."sitemap_urls"
    ADD CONSTRAINT "sitemap_urls_updated_by_fkey" FOREIGN KEY ("updated_by") REFERENCES "auth"."users"("id");



ALTER TABLE ONLY "public"."sitemap_urls"
    ADD CONSTRAINT "sitemap_urls_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id");



ALTER TABLE ONLY "public"."tasks"
    ADD CONSTRAINT "tasks_domain_id_fkey" FOREIGN KEY ("domain_id") REFERENCES "public"."domains"("id");



ALTER TABLE ONLY "public"."tasks"
    ADD CONSTRAINT "tasks_page_id_fkey" FOREIGN KEY ("page_id") REFERENCES "public"."pages"("id");



ALTER TABLE ONLY "public"."tenant_features"
    ADD CONSTRAINT "tenant_features_feature_id_fkey" FOREIGN KEY ("feature_id") REFERENCES "public"."feature_flags"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."tenant_features"
    ADD CONSTRAINT "tenant_features_tenant_id_fkey" FOREIGN KEY ("tenant_id") REFERENCES "public"."tenants"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."user_roles"
    ADD CONSTRAINT "user_roles_role_id_fkey" FOREIGN KEY ("role_id") REFERENCES "public"."roles"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."user_tenants"
    ADD CONSTRAINT "user_tenants_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id") ON DELETE CASCADE;



CREATE POLICY "Anyone can view features" ON "public"."features" FOR SELECT USING (true);



CREATE POLICY "Anyone can view votes" ON "public"."feature_votes" FOR SELECT USING (true);



CREATE POLICY "Authenticated users can create features" ON "public"."features" FOR INSERT WITH CHECK (("auth"."uid"() IS NOT NULL));



CREATE POLICY "Authenticated users can vote" ON "public"."feature_votes" FOR INSERT TO "authenticated" WITH CHECK (("user_id" = "auth"."uid"()));



CREATE POLICY "Tenants viewable by all authenticated users" ON "public"."tenants" FOR SELECT TO "authenticated" USING (true);



CREATE POLICY "Users can read their own profile" ON "public"."profiles" FOR SELECT USING (("auth"."uid"() = "id"));



CREATE POLICY "Users can remove their votes" ON "public"."feature_votes" FOR DELETE TO "authenticated" USING (("user_id" = "auth"."uid"()));



CREATE POLICY "Users can update their own profile" ON "public"."profiles" FOR UPDATE USING (("auth"."uid"() = "id"));



CREATE POLICY "Users can view profiles in their tenant" ON "public"."profiles" FOR SELECT USING ((("tenant_id" = "public"."current_user_tenant_id"()) AND ("role" = 'USER'::"text")));



CREATE POLICY "Users can view their own profile" ON "public"."profiles" FOR SELECT USING (("auth"."uid"() = "id"));



CREATE POLICY "pages_tenant_isolation" ON "public"."pages" USING (("tenant_id" = "auth"."uid"()));



CREATE POLICY "tasks_tenant_isolation" ON "public"."tasks" USING (("tenant_id" = "auth"."uid"()));



CREATE POLICY "user_tenants_read_own" ON "public"."user_tenants" FOR SELECT TO "authenticated" USING (("auth"."uid"() = "user_id"));



GRANT USAGE ON SCHEMA "public" TO "postgres";
GRANT USAGE ON SCHEMA "public" TO "anon";
GRANT USAGE ON SCHEMA "public" TO "authenticated";
GRANT USAGE ON SCHEMA "public" TO "service_role";



GRANT ALL ON FUNCTION "public"."current_user_tenant_id"() TO "anon";
GRANT ALL ON FUNCTION "public"."current_user_tenant_id"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."current_user_tenant_id"() TO "service_role";



GRANT ALL ON FUNCTION "public"."handle_feature_vote"() TO "anon";
GRANT ALL ON FUNCTION "public"."handle_feature_vote"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."handle_feature_vote"() TO "service_role";



GRANT ALL ON FUNCTION "public"."handle_new_user"() TO "anon";
GRANT ALL ON FUNCTION "public"."handle_new_user"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."handle_new_user"() TO "service_role";



GRANT ALL ON FUNCTION "public"."handle_updated_at"() TO "anon";
GRANT ALL ON FUNCTION "public"."handle_updated_at"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."handle_updated_at"() TO "service_role";



GRANT ALL ON FUNCTION "public"."update_modified_column"() TO "anon";
GRANT ALL ON FUNCTION "public"."update_modified_column"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."update_modified_column"() TO "service_role";



GRANT ALL ON FUNCTION "public"."update_updated_at_column"() TO "anon";
GRANT ALL ON FUNCTION "public"."update_updated_at_column"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."update_updated_at_column"() TO "service_role";



GRANT ALL ON FUNCTION "public"."user_has_permission"("permission_name" "text") TO "anon";
GRANT ALL ON FUNCTION "public"."user_has_permission"("permission_name" "text") TO "authenticated";
GRANT ALL ON FUNCTION "public"."user_has_permission"("permission_name" "text") TO "service_role";



GRANT ALL ON FUNCTION "public"."validate_permission_name"() TO "anon";
GRANT ALL ON FUNCTION "public"."validate_permission_name"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."validate_permission_name"() TO "service_role";



GRANT ALL ON TABLE "public"."alembic_version" TO "anon";
GRANT ALL ON TABLE "public"."alembic_version" TO "authenticated";
GRANT ALL ON TABLE "public"."alembic_version" TO "service_role";



GRANT ALL ON TABLE "public"."batch_jobs" TO "anon";
GRANT ALL ON TABLE "public"."batch_jobs" TO "authenticated";
GRANT ALL ON TABLE "public"."batch_jobs" TO "service_role";



GRANT ALL ON SEQUENCE "public"."batch_jobs_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."batch_jobs_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."batch_jobs_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."contacts" TO "anon";
GRANT ALL ON TABLE "public"."contacts" TO "authenticated";
GRANT ALL ON TABLE "public"."contacts" TO "service_role";



GRANT ALL ON TABLE "public"."domains" TO "anon";
GRANT ALL ON TABLE "public"."domains" TO "authenticated";
GRANT ALL ON TABLE "public"."domains" TO "service_role";



GRANT ALL ON TABLE "public"."feature_flags" TO "anon";
GRANT ALL ON TABLE "public"."feature_flags" TO "authenticated";
GRANT ALL ON TABLE "public"."feature_flags" TO "service_role";



GRANT ALL ON TABLE "public"."feature_votes" TO "anon";
GRANT ALL ON TABLE "public"."feature_votes" TO "authenticated";
GRANT ALL ON TABLE "public"."feature_votes" TO "service_role";



GRANT ALL ON TABLE "public"."features" TO "anon";
GRANT ALL ON TABLE "public"."features" TO "authenticated";
GRANT ALL ON TABLE "public"."features" TO "service_role";



GRANT ALL ON TABLE "public"."jobs" TO "anon";
GRANT ALL ON TABLE "public"."jobs" TO "authenticated";
GRANT ALL ON TABLE "public"."jobs" TO "service_role";



GRANT ALL ON TABLE "public"."jobs_backup" TO "anon";
GRANT ALL ON TABLE "public"."jobs_backup" TO "authenticated";
GRANT ALL ON TABLE "public"."jobs_backup" TO "service_role";



GRANT ALL ON SEQUENCE "public"."jobs_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."jobs_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."jobs_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."local_businesses" TO "anon";
GRANT ALL ON TABLE "public"."local_businesses" TO "authenticated";
GRANT ALL ON TABLE "public"."local_businesses" TO "service_role";



GRANT ALL ON TABLE "public"."migration_logs" TO "anon";
GRANT ALL ON TABLE "public"."migration_logs" TO "authenticated";
GRANT ALL ON TABLE "public"."migration_logs" TO "service_role";



GRANT ALL ON SEQUENCE "public"."migration_logs_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."migration_logs_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."migration_logs_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."pages" TO "anon";
GRANT ALL ON TABLE "public"."pages" TO "authenticated";
GRANT ALL ON TABLE "public"."pages" TO "service_role";



GRANT ALL ON TABLE "public"."permissions" TO "anon";
GRANT ALL ON TABLE "public"."permissions" TO "authenticated";
GRANT ALL ON TABLE "public"."permissions" TO "service_role";



GRANT ALL ON TABLE "public"."place_searches" TO "anon";
GRANT ALL ON TABLE "public"."place_searches" TO "authenticated";
GRANT ALL ON TABLE "public"."place_searches" TO "service_role";



GRANT ALL ON TABLE "public"."places_staging" TO "anon";
GRANT ALL ON TABLE "public"."places_staging" TO "authenticated";
GRANT ALL ON TABLE "public"."places_staging" TO "service_role";



GRANT ALL ON TABLE "public"."places_staging_backup" TO "anon";
GRANT ALL ON TABLE "public"."places_staging_backup" TO "authenticated";
GRANT ALL ON TABLE "public"."places_staging_backup" TO "service_role";



GRANT ALL ON SEQUENCE "public"."places_staging_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."places_staging_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."places_staging_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."profiles" TO "anon";
GRANT ALL ON TABLE "public"."profiles" TO "authenticated";
GRANT ALL ON TABLE "public"."profiles" TO "service_role";



GRANT ALL ON TABLE "public"."role_permissions" TO "anon";
GRANT ALL ON TABLE "public"."role_permissions" TO "authenticated";
GRANT ALL ON TABLE "public"."role_permissions" TO "service_role";



GRANT ALL ON TABLE "public"."roles" TO "anon";
GRANT ALL ON TABLE "public"."roles" TO "authenticated";
GRANT ALL ON TABLE "public"."roles" TO "service_role";



GRANT ALL ON SEQUENCE "public"."roles_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."roles_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."roles_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."sidebar_features" TO "anon";
GRANT ALL ON TABLE "public"."sidebar_features" TO "authenticated";
GRANT ALL ON TABLE "public"."sidebar_features" TO "service_role";



GRANT ALL ON TABLE "public"."sitemap_files" TO "anon";
GRANT ALL ON TABLE "public"."sitemap_files" TO "authenticated";
GRANT ALL ON TABLE "public"."sitemap_files" TO "service_role";



GRANT ALL ON TABLE "public"."sitemap_files_backup" TO "anon";
GRANT ALL ON TABLE "public"."sitemap_files_backup" TO "authenticated";
GRANT ALL ON TABLE "public"."sitemap_files_backup" TO "service_role";



GRANT ALL ON TABLE "public"."sitemap_urls" TO "anon";
GRANT ALL ON TABLE "public"."sitemap_urls" TO "authenticated";
GRANT ALL ON TABLE "public"."sitemap_urls" TO "service_role";



GRANT ALL ON TABLE "public"."task_analytics" TO "anon";
GRANT ALL ON TABLE "public"."task_analytics" TO "authenticated";
GRANT ALL ON TABLE "public"."task_analytics" TO "service_role";



GRANT ALL ON TABLE "public"."task_history" TO "anon";
GRANT ALL ON TABLE "public"."task_history" TO "authenticated";
GRANT ALL ON TABLE "public"."task_history" TO "service_role";



GRANT ALL ON TABLE "public"."tasks" TO "anon";
GRANT ALL ON TABLE "public"."tasks" TO "authenticated";
GRANT ALL ON TABLE "public"."tasks" TO "service_role";



GRANT ALL ON TABLE "public"."tenant_features" TO "anon";
GRANT ALL ON TABLE "public"."tenant_features" TO "authenticated";
GRANT ALL ON TABLE "public"."tenant_features" TO "service_role";



GRANT ALL ON TABLE "public"."tenants" TO "anon";
GRANT ALL ON TABLE "public"."tenants" TO "authenticated";
GRANT ALL ON TABLE "public"."tenants" TO "service_role";



GRANT ALL ON TABLE "public"."user_roles" TO "anon";
GRANT ALL ON TABLE "public"."user_roles" TO "authenticated";
GRANT ALL ON TABLE "public"."user_roles" TO "service_role";



GRANT ALL ON TABLE "public"."user_tenants" TO "anon";
GRANT ALL ON TABLE "public"."user_tenants" TO "authenticated";
GRANT ALL ON TABLE "public"."user_tenants" TO "service_role";



ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "service_role";






ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "service_role";






ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "service_role";






RESET ALL;
