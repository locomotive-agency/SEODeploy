# SEO Testing Config File


# Content King API
CMS_API_KEY    = "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
REPORT_API_KEY = "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
ENDPOINT       = "https://api.contentkingapp.com/v1/"
API_TIMEOUT    = 20
PER_PAGE       = 300
TIMEZONE       = 'Europe/Amsterdam'
THREADS        = 5
BATCH_SIZE     = 10
BATCH_WAIT     = 10
TIME_COL       = "unstable_last_checked_at"

# Sample URLs
CONFIDENCE_LEVEL    = 95.0
CONFIDENCE_INTERVAL = 5.0
URL_LIMIT           = 1000
SAMPLES_FILENAME    = 'path_samples.txt'

# Servers
# Site_Ids can be found in the URL of the website in ContentKing: Eg. https://app.contentkingapp.com/websites/**7-324470**/dashboard

PROD_HOST     = 'https://locomotive.agency'
PROD_SITE_ID  = '7-453638'

STAGE_HOST    = 'https://locomotive.agency'
STAGE_SITE_ID = '7-453638'

# Logging
LOG_FILE = "seotesting.log"



# Issues Checking Exclusions
IGNORE_ISSUES = {
    "analytics/analytics_missing" : False,
    "analytics/visual_analytics_missing" : False,
    "h1/duplicate" : False,
    "h1/incorrect_length" : False,
    "h1/missing" : False,
    "h1/too_many" : False,
    "canonical_link/incorrectly_canonicalized" : False,
    "canonical_link/missing" : False,
    "canonical_link/points_to_unindexable" : False,
    "canonical_link/too_many" : False,
    "images/alt_attribute" : False,
    "images/title_attribute" : False,
    "links/broken" : False,
    "links/redirected" : False,
    "links/to_canonicalized" : False,
    "meta_description/duplicate" : False,
    "meta_description/incorrect_length" : False,
    "meta_description/missing" : False,
    "meta_description/too_many" : False,
    "title/duplicate" : False,
    "title/incorrect_length" : False,
    "title/missing" : False,
    "title/too_many" : False,
    "open_graph/description_incorrect_length" : False,
    "open_graph/description_missing" : False,
    "open_graph/image_missing" : False,
    "open_graph/title_incorrect_length" : False,
    "open_graph/title_missing" : False,
    "open_graph/url_missing" : False,
    "twitter_cards/description_incorrect_length" : False,
    "twitter_cards/description_missing" : False,
    "twitter_cards/image_missing" : False,
    "twitter_cards/site_missing" : False,
    "twitter_cards/title_incorrect_length" : False,
    "twitter_cards/title_missing" : False,
    "twitter_cards/type_invalid" : False,
    "twitter_cards/type_missing" : False,
    "xml_sitemap/incorrectly_missing" : False,
    "xml_sitemap/incorrectly_present" : False
}


# COntent Checking Exclusions
IGNORE_CONTENT = {
    "canonical" : False,
    "title" : False,
    "meta_description" : False,
    "h1" : False,
    "h2" : False,
    "meta_robots" : False,
    "open_graph_description" : False,
    "open_graph_image" : False,
    "open_graph_title" : False,
    "open_graph_type" : False,
    "open_graph_url" : False,
    "twitter_card" : False,
    "twitter_site" : False,
    "google_analytics" : False

}
