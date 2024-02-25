from .connection import collection


def activity_selection(request):
    newdata = list(collection.find({},{'_id':0}).sort('departure_timestamp', 1))
    platform = {}
    delay_time_min = 0
    platform_priority = []
    pattern = ['1', '2', '3', '4']
    remaining_activity = newdata[:]
    post_values = list(request.POST.values())
    post_values.pop(0)

    for i in post_values:
        if i in pattern:
            platform_priority.append(int(i))
            pattern.remove(i)
    count = 0

    def helper(count, discarded_activities):

        if count == len(platform_priority) or len(discarded_activities) == 0:
            return discarded_activities

        selected_activities = []
        for activity in discarded_activities:
            if len(selected_activities) == 0:
                selected_activities.append(activity)
            else:
                if activity['arrival_timestamp'] >= selected_activities[-1]['departure_timestamp']+(delay_time_min*60):
                    selected_activities.append(activity)
        for i in selected_activities:
            discarded_activities.remove(i)
        platform[platform_priority[count]] = selected_activities
        return helper(count+1, discarded_activities)

    remaining_activity = helper(count, remaining_activity)
    return platform, remaining_activity
