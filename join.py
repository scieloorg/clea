def aff_contrib_full_outer_join_dframe(article):
    import pandas as pd
    return pd.merge(pd.DataFrame(article.data["aff"]),
                    pd.DataFrame(article.data["contrib"]),
                    left_on="aff_id", right_on="xref_aff",
                    how="outer")
