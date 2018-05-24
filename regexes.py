import regex


def bm_regex(regex_string):
    """Compile best multiline regex."""
    return regex.compile(regex_string, regex.B | regex.M)


FRONT_TAG_PATH_REGEXES = {
    "article-meta": regex.compile(
        r"/(?:front){e<=1}"
        r"/(?:.*/)?(?:article-meta){e<=2}$"
    ),
    "journal-meta": regex.compile(
        r"/(?:front){e<=1}"
        r"/(?:.*/)?(?:journal-meta){e<=2}$"
    ),
    "contrib": regex.compile(
        r"/(?:front){e<=1}"
        r"/(?:.*/)?(?:article-meta){e<=4}"
        r"/(?:.*/)?(?:contrib){e<=2}$"
    ),
    "aff": regex.compile(
        r"/(?:front){e<=1}"
        r"/(?:.*/)?(?:article-meta){e<=4}"
        r"/(?:.*/)?(?:aff){e<=1}$"
    ),
}

BRANCH_REGEXES = {
    "article-meta": [
        ("article_doi", "", bm_regex(
            r"/(?:article-id){e<=2}(?:@[^/]*)?"
            r"@(?:pub-id-type){e<=4}"
            r"=(?:doi){e<=1}(?:@[^/]*)?$"
        )),
        ("article_publisher_id", "", bm_regex(
            r"/(?:article-id){e<=2}(?:@[^/]*)?"
            r"@(?:pub-id-type){e<=4}"
            r"=(?:publisher-id){e<=4}(?:@[^/]*)?$"
        )),
        ("article_title", "", bm_regex(r"/(?:article-title){e<=2}$")),
    ],
    "journal-meta": [
        ("issn_epub", "", bm_regex(
            r"/(?:issn){e<=1}(?:@[^/]*)?"
            r"@(?:pub-type){e<=3}"
            r"=e(?:pub){e<=1}(?:@[^/]*)?$"
        )),
        ("issn_ppub", "", bm_regex(
            r"/(?:issn){e<=1}(?:@[^/]*)?"
            r"@(?:pub-type){e<=3}"
            r"=p(?:pub){e<=1}(?:@[^/]*)?$"
        )),
        ("journal_nlm_ta", "", bm_regex(
            r"/(?:journal-id){e<=2}(?:@[^/]*)?"
            r"@(?:journal-id-type){e<=5}"
            r"=(?:nlm-ta){e<=2}(?:@[^/]*)?$"
        )),
        ("journal_publisher_id", "", bm_regex(
            r"/(?:journal-id){e<=2}(?:@[^/]*)?"
            r"@(?:journal-id-type){e<=5}"
            r"=(?:publisher-id){e<=4}(?:@[^/]*)?$"
        )),
        ("journal_title", "", bm_regex(r"/(?:journal-title){e<=2}$")),
        ("publisher_name", "", bm_regex(r"/(?:publisher-name){e<=3}$")),
    ],
    "contrib": [
        ("contrib_bio", "", bm_regex(r"/(?:bio){e<=1}$")),
        ("contrib_degrees", "", bm_regex(r"/(?:degrees){e<=2}$")),
        ("contrib_email", "", bm_regex(r"/(?:email){e<=1}$")),
        ("contrib_name", "", bm_regex(r"/(?:name){e<=1}$")),
        ("contrib_given_names", "", bm_regex(r"/(?:given-names){e<=3}$")),
        ("contrib_orcid", "", bm_regex(
            r"/(?:contrib-id){e<=2}(?:@[^/]*)?"
            r"@(?:contrib-id-type){e<=7}"
            r"=(?:orcid){e<=1}(?:@[^/]*)?$"
        )),
        ("contrib_prefix", "", bm_regex(r"/(?:prefix){e<=2}$")),
        ("contrib_role", "", bm_regex(r"/(?:role){e<=1}$")),
        ("contrib_suffix", "", bm_regex(r"/(?:suffix){e<=2}$")),
        ("contrib_surname", "", bm_regex(r"/(?:surname){e<=2}$")),
        ("contrib_type", "contrib-type", bm_regex(
            r"/(?:contrib){e<=2}(?:@[^/]*)?"
            r"@(?:contrib-type){e<=5}=[^/]*$"
        )),
        ("xref_corresp", "rid", bm_regex(
            r"/(?:xref){e<=1}(?:@[^/]*)?"
            r"@(?:ref-type){e<=2}"
            r"=(?:corresp){e<=2}(?:@[^/]*)?$"
        )),
        ("xref_corresp_text", "", bm_regex(
            r"/(?:xref){e<=1}(?:@[^/]*)?"
            r"@(?:ref-type){e<=2}"
            r"=(?:corresp){e<=2}(?:@[^/]*)?$"
        )),
        ("xref_aff", "rid", bm_regex(
            r"/(?:xref){e<=1}(?:@[^/]*)?"
            r"@(?:ref-type){e<=2}"
            r"=(?:aff){e<=1}(?:@[^/]*)?$"
        )),
        ("xref_aff_text", "", bm_regex(
            r"/(?:xref){e<=1}(?:@[^/]*)?"
            r"@(?:ref-type){e<=2}"
            r"=(?:aff){e<=1}(?:@[^/]*)?$"
        )),
    ],
    "aff": [
        ("addr_city", "", bm_regex(
            r"/(?:city){e<=1}$|"
            r"/(?:named-content){e<=4}(?:@[^/]*)?"
            r"@(?:content-type){e<=4}"
            r"=(?:city){e<=1}(?:@[^/]*)?$"
        )),
        ("addr_country", "", bm_regex(r"/(?:country){e<=2}(?:@[^/]*)?$")),
        ("addr_country_code", "country", bm_regex(
            r"/(?:country){e<=2}(?:@[^/]*)?"
            r"@(?:country){e<=4}[=-][^/]*$"
        )),
        ("addr_postal_code", "", bm_regex(
            r"/(?:postal-code){e<=3}$|"
            r"/(?:named-content){e<=4}(?:@[^/]*)?"
            r"@(?:content-type){e<=4}"
            r"=(?:zipcode){e<=2}(?:@[^/]*)?$"
        )),
        ("addr_state", "", bm_regex(
            r"/(?:state){e<=2}$|"
            r"/(?:named-content){e<=4}(?:@[^/]*)?"
            r"@(?:content-type){e<=4}"
            r"=(?:state){e<=2}(?:@[^/]*)?$"
        )),
        ("aff_id", "id", bm_regex(
            r"/(?:aff){e<=1}(?:@[^/]*)?"
            r"@(?:id){e<=1}=[^/]*$"
        )),
        ("aff_text", "", bm_regex(r"/(?:aff){e<=1}(?:@[^/]*)?$")),
        ("aff_email", "", bm_regex(r"/(?:email){e<=1}$")),
        ("institution_original", "", bm_regex(
            r"/(?:institution){e<=2}(?:@[^/]*)?"
            r"@(?:content-type){e<=4}"
            r"=(?:original){e<=2}(?:@[^/]*)?$"
        )),
        ("institution_orgdiv1", "", bm_regex(
            r"/(?:institution){e<=2}(?:@[^/]*)?"
            r"@(?:content-type){e<=4}"
            r"=(?:orgdiv){e<=2}1(?:@[^/]*)?$"
        )),
        ("institution_orgdiv2", "", bm_regex(
            r"/(?:institution){e<=2}(?:@[^/]*)?"
            r"@(?:content-type){e<=4}"
            r"=(?:orgdiv){e<=2}2(?:@[^/]*)?$"
        )),
        ("institution_orgname", "", bm_regex(
            r"/(?:institution){e<=2}(?:@[^/]*)?"
            r"@(?:content-type){e<=4}"
            r"=(?:orgname){e<=2}(?:@[^/]*)?$"
        )),
        ("institution_orgname_rewritten", "", bm_regex(
            r"/(?:institution){e<=2}(?:@[^/]*)?"
            r"@(?:content-type){e<=4}"
            r"=(?:normalized){e<=4}(?:@[^/]*)?$"
        )),
        ("label", "", bm_regex(r"/(?:label){e<=1}$")),
        ("phone", "", bm_regex(r"/(?:phone){e<=1}$")),
    ],
}
