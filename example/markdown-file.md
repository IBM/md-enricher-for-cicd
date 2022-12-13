---

copyright:
  years: 2022, [{CURRENT_YEAR}]
lastupdated: "[{LAST_UPDATED_DATE}]"

keywords: test, file
subcollection: test

---

<!--The metadata styling and markdown structure is defined by the marked-it markdown processor: https://ibm.github.io/marked-it/#/ 
-->

# Test file for <staging>staging</staging><prod>prod</prod>
{: #test}

This file includes example text.
{: shortdesc}
<new-feature>

## New feature
{: #new-feature}

This section documents a new feature. Display this section in staging, but not in prod yet.
{: shortdesc}
</new-feature><old-feature>

## Old feature
{: #old-feature}

This section documents an old feature. Display this section in prod only.
{: shortdesc}</old-feature>


## Existing feature

This section is about a feature that's been here for awhile, so it should be in both staging and prod.
{: shortdesc}<hidden>


## Hidden section
{: #hidden}

This is a hidden section. It will not display in any of the output.
{: shortdesc}</hidden>


## Images
{: #images}

![An image that displays in both staging and prod](images/both.svg "Both")
<staging>![An image that displays in staging, but not prod](images/staging.svg "Staging")</staging>
<prod>![An image that displays in prod, but not staging](images/prod.svg "Prod")</prod>


## Reuse snippets
{: #snippets}

You can include a phrase or sentence like {[product-name]} {[version]} from reuse-snippets/phrases.json or a whole markdown topic that is also stored in reuse-snippets folder.

{[table.md]}
