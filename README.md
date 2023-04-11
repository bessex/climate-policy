# How does media representation of climate policy impact political outcomes?

## Project Overview

This project aims to investigate the relationship between media representation of climate policy and its impact on political outcomes. We utilize a corpus of news articles labeled pulled from AYLIEN, and annotate articles according to the bias of the news source (as given by AllSides.com). By applying clustering and regression techniques, as well as sentiment analysis, we aim to uncover potential correlations between media coverage and political outcomes in the context of climate policy.

## Dataset

Our primary dataset is corpus of articles we acquired from AYLIEN, and media bias ratings from AllSides.com. Additionally, we utilize congressional voting data acquired from the ProPublica Congress API to correlate media representation with political outcomes. Sentiment analysis was performed using the FLAN-T5-xl model with 3x19 shot learning. (See more in final report).

## Progress

### Data Collection & Preprocessing

- Completion of data gathering tasks one week behind schedule
- Data processing and transformation completed in the following week
- Manual annotation of data for bias/sentiment and initial data analysis began

### Data Analysis

- Acquired 40k+ articles pertaining to climate policy using the AYLIEN News API
- Associated media source bias with each document using the AllSideR dataset
- Performed basic statistics to analyze voting results based on political party for bills related to climate change policy
- Analyzed the proportion of Democrat and Republican Congress votes for climate policy across time
- Complete manual annotation of 56 document window instances
- Perform sentiment analysis using FLAN-T5-xl

## Next Steps
- Perform a regression model on sentiment and proportion of "yea" votes to determine the impact of media sentiment on climate policy passing in Congress
- If time permits, compute a regression model for media bias versus sentiment on climate policy and cluster news sources with media bias and sentiment using dimensionality-reduction techniques

## Sources

- Hugging Face Model: `google/flan-t5-xl`
- AllSides.com source rankings
- ProPublica Congress API
- AYLIEN News API
