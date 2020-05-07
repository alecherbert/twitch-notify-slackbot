import peewee as pw


db = pw.SqliteDatabase('following.db')

class User(pw.Model):
    display_name = pw.CharField()
    user_id = pw.IntegerField()
    profile_image = pw.CharField()
    last_subscribed = pw.TimestampField(null=True,default=None)
    last_live = pw.TimestampField(null=True,default=None)

    class Meta:
        database = db
