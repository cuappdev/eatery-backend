# eatery-backend

An open-sourced backend for the Eatery application, available on Android and iOS.

Technologies involved include:

1. Flask
2. GraphQL

## Virtualenv

Virtualenv setup!

```bash
virtualenv -p python3.7 venv
source venv/bin/activate
pip install -r requirements.txt
```

## Environment Variables

It's recommended to use [`direnv`](https://direnv.net).
The required environment variables for this API are the following:

To use `direnv` with this repository, run the following and set the variables appropriately.

```bash
cp envrc.template .envrc
```

## Setting up linter

**Flake 8**: Install [flake8](http://flake8.pycqa.org/en/latest/)

**Black**: Either use [command line tool](https://black.readthedocs.io/en/stable/installation_and_usage.html) or use [editor extension](https://black.readthedocs.io/en/stable/editor_integration.html).

If using VS Code, install the 'Python' extension and include following snippet inside `settings.json`:

```json
"python.linting.pylintEnabled": false,
"python.linting.flake8Enabled": true,
"python.formatting.provider": "black"
```

---

## Running the App

```bash
sh start_server.sh
```

The flask app runs on your ['localhost'](http://localhost:5000/) via port 5000.

\*NOTE: App may take up some time before starting because it needs to fetch and parse data at start up.

---

## Notes

- `src.database` : models for db
- `src.eatery_db` : parse raw data and store into db
- `src.gql_parser` : fetch data from db and put into graphQL types
- `src.gql_types` : graphQL types

---

## Data Updates

### Campus Eateries

Campus eateries are updated at app start-up **and** at regularly scheduled hours.

Regular updates are scheduled as cron job in `update_db.txt`. Note that cron uses UTC timezone so ` 0 9,15,21 * * *` refers to daily updates at 5AM, 11AM, 5PM EST. The updates are scheduled at hours within close range of dining hall opening hours because dining hall menus are updated by Cornell at random times.

### Collegetown Eateries

Collegetown updates are run **only** at app start-up since data on Yelp doesn't change frequently. To run manual updates, execute `python update_ctown.py` in docker container.

Also refer to [#193](https://github.com/cuappdev/eatery-backend/pull/193) to see why ctown update isn't scheduled as cron job.

---

## API Spec

### /hello • GET

Hello, World!

### / • GET

This endpoint gives graphQL interface, GraphiQL, where you can construct queries and request data. Refer to the documentation in GraphiQL to view the nested data structure of query.

---

## GraphQL Interface

### Example query 1 :

This should show names of all campus eateries in database.

```
{
  campusEateries {
    name
  }
}
```

### Example query 2 :

This should be an extensive query that contains (almost) all the nested fields for eateries.

```
{
  campusEateries {
    coordinates {
      latitude
      longitude
    }
    eateryType
    id
    imageUrl
    name
    paymentMethods {
      brbs
      cash
      cornellCard
      credit
      mobile
      swipes
    }
    paymentMethodsEnums
    phone
    about
    campusArea {
      descriptionShort
    }
    expandedMenu {
      category
      stations {
        category
        items {
          item
          healthy
          choices {
            label
            options
          }
          price
        }
      }
    }
    location
    nameShort
    operatingHours {
      date
      events {
        calSummary
        description
        endTime
        menu {
          category
          items {
            item
            healthy
          }
        }
        startTime
      }
    }
    slug
    swipeData {
      endTime
      sessionType
      startTime
      swipeDensity
      waitTimeHigh
      waitTimeLow
    }
  }
  collegetownEateries{
    coordinates{
      latitude
      longitude
    }
    eateryType
    id
    imageUrl
    name
    paymentMethods {
      brbs
      cash
      cornellCard
      credit
      mobile
      swipes
    }
    paymentMethodsEnums
    phone
    address
    categories
    operatingHours{
            date
      events {
        description
        endTime
        startTime
      }
    }
    price
    rating
    ratingEnum
    url
  }
}
```
