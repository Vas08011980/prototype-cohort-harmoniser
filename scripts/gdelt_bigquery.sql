-- GDELT news-attention counts for the Cohort Harmoniser "invisible room"   (v3, multilingual, entity-decoded)
-- Run in Google BigQuery. Project: project-5b1b70dc-8e21-4c5a-ab4 (Vasileios, free trial).
-- Lookup table gdelt.domains = GDELT MASTER-GDELTDOMAINSBYCOUNTRY-MAY2018.TXT, filtered to the
-- 8 target countries (FIPS US, AS, UK, EI, NZ, NO, GR, KS); columns domain, fips, country.
--
-- Titles in GKG Extras are HTML-entity encoded; a JS UDF decodes them before matching.
-- Matching is on page title (GKG Extras <PAGE_TITLE>) + URL; GKG holds no article full text.
-- Keywords: English + Greek + Korean + Norwegian. Non-English terms were drafted by Claude and
-- need checking by native speakers (Greek: Vasileios; Korean, Norwegian: not yet checked).
-- Norwegian "spillavhengighet" (= gambling addiction) is deliberately excluded.
-- Output: raw counts per country-year; shares (n_topic / n_total) are computed afterwards.

CREATE TEMP FUNCTION decode_entities(s STRING) RETURNS STRING LANGUAGE js AS r"""
  if (s === null) return null;
  const cp = n => (n > 0 && n <= 0x10FFFF) ? String.fromCodePoint(n) : ' ';  // skip invalid codes
  return s.replace(/&#x([0-9a-fA-F]{1,6});/g, (m, h) => cp(parseInt(h, 16)))
          .replace(/&#([0-9]{1,7});/g, (m, d) => cp(parseInt(d, 10)))
          .replace(/&amp;/g, '&').replace(/&quot;/g, '"').replace(/&#39;|&apos;/g, "'");
""";

WITH arts AS (
  SELECT DISTINCT
    DIV(DATE, 10000000000) AS year,
    LOWER(SourceCommonName) AS domain,
    DocumentIdentifier AS url,
    REGEXP_EXTRACT(Extras, r'<PAGE_TITLE>(.*?)</PAGE_TITLE>') AS title_raw
  FROM `gdelt-bq.gdeltv2.gkg_partitioned`
  WHERE _PARTITIONTIME >= TIMESTAMP('2017-01-01')
    AND _PARTITIONTIME <  TIMESTAMP('2026-01-01')
),
j AS (
  -- titles are stored with HTML numeric entities (Greek, Korean etc.); decode after the join
  SELECT a.year, d.fips,
         LOWER(CONCAT(IFNULL(decode_entities(a.title_raw), ''), ' ', a.url)) AS txt
  FROM arts a
  JOIN `project-5b1b70dc-8e21-4c5a-ab4.gdelt.domains` d ON a.domain = LOWER(d.domain)
)
SELECT
  fips, year,
  COUNT(*) AS n_total,
  COUNTIF(REGEXP_CONTAINS(txt, r'social.?media|κοινωνικ\S* δ[ιί]κτ|소셜 ?미디어|(^|[^a-z])sns([^a-z]|$)|sosiale? medi')
      AND REGEXP_CONTAINS(txt, r'child|teen|adolescen|youth|kids|παιδ|αν[ηή]λικ|[εέ]φηβ|청소년|아동|어린이|10대|미성년|barn|ungdom|tenåring')) AS n_youth_social_media,
  COUNTIF(REGEXP_CONTAINS(txt, r'screen.?time|χρ[οό]ν\S* οθ[οό]ν|스크린 ?타임|화면 ?시간|skjermtid')) AS n_screen_time,
  COUNTIF(REGEXP_CONTAINS(txt, r'cyber.?bull|(διαδικτυακ|ηλεκτρονικ|κυβερνο)\S*\s?εκφοβισμ|사이버 ?(폭력|괴롭힘|불링|따돌림)|nettmobb|digital mobbing')) AS n_cyberbullying,
  COUNTIF(REGEXP_CONTAINS(txt, r'online.?safety|διαδικτυακ\S* ασφ[αά]λει|ασφ[αά]λει\S* (στο|του) διαδ[ιί]κτυ|온라인 ?안전|nettsikkerhet|trygg\S* på nett')) AS n_online_safety,
  COUNTIF(REGEXP_CONTAINS(txt, r'chatgpt|generative.?ai|παραγωγικ\S* τεχνητ|생성형 ?(ai|인공지능)|챗 ?gpt|챗지피티|generativ.?(ki|kunstig)')) AS n_generative_ai,
  COUNTIF(REGEXP_CONTAINS(txt, r'gaming.?(disorder|addiction)|video.?game.?addiction|εθισμ\S* (στα |στο |στον )?(ηλεκτρονικ\S* |βιντεο)?παιχν|게임 ?(중독|이용 ?장애|과몰입)|dataspillavhengig|gamingavhengig')) AS n_gaming_addiction
FROM j
GROUP BY fips, year
ORDER BY fips, year;
