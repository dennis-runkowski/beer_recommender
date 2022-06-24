"""Model to store stats in the main db."""
import operator
from datetime import datetime, timedelta

from flask_app.extensions import db
from sqlalchemy import func
from sqlalchemy import extract


class TrackModel(db.Model):
    """Class to save cold one stats for each user."""

    __tablename__ = 'track'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    drink_type = db.Column(db.String(80), nullable=False)
    quantity = db.Column(db.String(80), nullable=False)
    location = db.Column(db.String(80), nullable=False)
    state = db.Column(db.String(80), nullable=False)
    date_time = db.Column(db.DateTime(), nullable=False)

    def __init__(self, username, drink_type, quantity, location,
                 state, date_time):
        self.username = username
        self.drink_type = drink_type
        self.quantity = quantity
        self.location = location
        self.state = state
        self.date_time = date_time

    def save_to_db(self):
        """Method to save user to the db."""
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username):
        """Class method to query by id."""
        return cls.query.filter_by(username=username).first()

    @classmethod
    def user_rank(cls, username):
        """
        Get the users rank and total number of users

        Args:
            username (str): username you want the rank for

        Returns:
            dict with rank, total_cold_ones total number of users

        Example
            {
                "rank": 2,
                "total": 10,
                "total_cold_ones": 40
            }

        """
        cold_one_count = cls.query.with_entities(
            cls.username,
            func.sum(cls.quantity).label('quantity')
        ).group_by(cls.username)

        # total_users = cls.query.with_entities(cls.username).distinct()
        # print(len([i.username for i in total_users]))
        res = []
        for i in cold_one_count:
            res.append({"username": i.username, "count": i.quantity})

        # sort(res, key=lambda k: k['count'], reverse=True)
        res.sort(key=operator.itemgetter('count'), reverse=True)

        final_res = {}
        for idx, i in enumerate(res):
            if i.get("username") == username:
                final_res["rank"] = idx + 1
                final_res["total_cold_ones"] = i.get("count")
                break
        final_res["total"] = len(res)

        if not final_res.get("rank"):
            final_res["rank"] = len(res)
            final_res["total_cold_ones"] = 0

        return final_res

    @classmethod
    def total_by_date(cls, username, num_days=7):
        """
        Get the total cold ones for the past n days. Default is
        set to 7 days

        Args:
            username (str): username
            num_days (int): Number of days to get the total for.

        Returns:
            dict with the week total cold ones for a user

        Example
            {
                "week_total": 10
            }

        """
        date_range = datetime.now() - timedelta(days=num_days)
        data = cls.query.with_entities(
            cls.username,
            func.sum(cls.quantity).label('quantity')
        ).filter_by(
            username=username).filter(cls.date_time >= date_range).first()

        if data.quantity:
            total = data.quantity
        else:
            total = 0
        res = {"week_total": total}

        return res


    @classmethod
    def total_by_type(cls):
        """
        Aggregate the total number of cold ones by type

        Returns:
            dict with the type as the key and sum as the value

        """
        data = cls.query.with_entities(
            cls.drink_type,
            func.sum(cls.quantity).label('quantity')
        ).group_by(cls.drink_type)

        res = [{"type": i.drink_type, "count": i.quantity} for i in data]
        res.sort(key=operator.itemgetter('count'), reverse=True)

        return res

    @classmethod
    def average_by_week(cls, username):
        """
        Average cold ones for a user by week

        Args:
            username (str): username
        Returns:
            int
        """
        data = cls.query.with_entities(
            extract('week', cls.date_time),
            func.sum(cls.quantity).label('quantity')
        ).group_by(extract('week', cls.date_time)).filter_by(username=username)

        stats = []
        for i in data:
            stats.append(i.quantity)

        try:
            weeks = len(stats)
            total = sum(stats)
            average = round(total / weeks)
        except:
            average = "N/A"

        return average

    @classmethod
    def get_time_series(cls, username):
        """
        Get time series data for one user

        Args:
            username (str): user name

        Returns:
            list of dicts containing date and amount of cold ones

        """
        # func.date_format(cls.date_time, "%Y-%m-%d")
        data = cls.query.with_entities(
            cls.date_time,
           cls.quantity
        ).filter_by(username=username).order_by(cls.date_time)

        if data:
            # Python 3.6 uses ordered dicts
            stats = {}
            for i in data:
                date_str = i.date_time.strftime("%Y-%m-%d")
                if stats.get(date_str):
                    stats[date_str] += int(i.quantity)
                else:
                    stats[date_str] = int(i.quantity)

            res = []
            for k, v in stats.items():
                temp = {
                    "date": k,
                    "amount": v
                }
                res.append(temp)
        else:
            res = False
        return res

    @classmethod
    def aggregate_by_state(cls, username=None):
        """
        Aggregate cold ones by stat
        Args:
            username (str): default is none

        Returns:
            dict

        Examples
            {
                "NY": 10,
                "SC": 50,
            }
        """
        data = cls.query.with_entities(
            cls.state,
            func.sum(cls.quantity).label("quantity")
        ).group_by(cls.state)

        if data:
            res = {i.state: i.quantity for i in data}
        else:
            res = False

        return res

    @classmethod
    def paginate_results(cls, username, page_number=1, per_page=10):
        """
        Paginate through a users cold ones
        Args:
            username (str): username
            page_number (int): the page number you want to return
            per_page (int): number of rows per page

        Returns:
            list of dicts with all the data

        """

        page = cls.query.filter_by(username=username).order_by(
            cls.date_time.desc()).paginate(
            per_page=per_page,
            page=page_number
        )
        page_data = []
        for i in page.items:
            temp = {}
            temp["date"] = i.date_time.strftime("%Y-%m-%d")
            temp["location"] = i.location
            temp["username"] = i.username
            temp["type"] = i.drink_type
            temp["quantity"] = i.quantity
            page_data.append(temp)

        res = {}
        res["current_page"] = page.page
        res["next_page"] = page.next_num
        res["prev_page"] = page.prev_num
        res["total_pages"] = page.pages
        res["data"] = page_data

        return res
