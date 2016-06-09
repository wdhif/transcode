Meteor.publish('profile', function () {
    if (!this.userId) {
        return [];
    }

    return Meteor.users.find({
        _id: this.userId
    });
});
