![Build and Test mycollect](https://github.com/mathrb/mycollect/workflows/Build%20and%20Test%20mycollect/badge.svg?branch=master)

# MyCollect

Mycollect monitor social networks to find the information the user is looking for.

## Getting started

Requirements:

* python >= 3.8
* [pipenv](https://pipenv.pypa.io/en/latest/)

`pipenv install` will create and install all required modules.

### Configuration

Rename sample_config.yaml to config.yaml

Update the config.yaml with your [twitter api credentials](twitter-api-credentials).

The email sender requires an [AWS account](aws-account), and will use the SES service, which allows 62k emails per month (should be enough).

### Start the collect

`pipenv run python -m mycollect.starter`

## Configuring the collect

You can configure the twitter collect:

* languages: list of languages of the tweets
* low_priority_url: prioritize URLs in tweets which have a different hostname from the list
* track: list of terms you want to follow

## Configuring the storage

Currently only file storage is implemented. You can specify the folder where the files will be stored:

```yaml
storage:
  type: mycollect.storage.file_storage.FileStorage
  args:
    folder: STORAGE_FOLDER
```

## Configuring aggregators

Currently there is only one aggregator: DummyAggregator, that will group elements per URL and category,
and electing the top x per category

```yaml
aggregators:
  - name: dummy aggregator
    type: mycollect.aggregators.dummy_aggregator.DummyAggregator
    schedule: 30 18 * * *
    notify: daily_report
    args:
      top_articles: 3
```

The schedule parameter is used to trigger the aggregator.
The notify property is used to trigger the right output

## Configuring output

### Email

* recipients: the list of emails you want to send an email to
* sender: the email address that is used as the sender
* templates: jinja2 templates of the email body

A template should have a name and a template, the name should match one of the notify property in aggregators.

## Annexes

### Twitter api credentials

If you don't have a twitter developer account: [link](https://developer.twitter.com/en/apply)

Create a twitter application: [link](https://developer.twitter.com/en/apps)

From the Keys and tokens tab, you will find the credentials:

* Consumer API keys
  * api key
  * api secret key
* Access token & access token secret
  * access token
  * access token secret

### AWS account

I suggest you to read the [AWS documentation](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/sign-up-for-aws.html), which contains:

* creation of the account
* configuring the service


Once done, get:
* aws access key
* aws secret key
* aws region of the SES service (it might depend on your location)
