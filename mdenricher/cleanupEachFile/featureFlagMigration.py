def featureFlagMigration(self, details):

    import json
    from operator import itemgetter

    newJSON = []
    self.log.debug('Restructuring feature flag file for: ' + self.location_name)

    featureFlags = sorted(details['featureFlags'], key=itemgetter('name'))

    for featureFlag in featureFlags:
        featureFlag_name = featureFlag['name']
        featureFlag_locations = featureFlag['location']

        if self.location_name in featureFlag_locations:
            featureFlag_locations_list = featureFlag_locations.split(',')
            new_locations = []
            for featureFlag_locations_entry in featureFlag_locations_list:
                if self.location_name + '-draft' in featureFlag_locations_entry:
                    new_locations.append('draft')
                elif self.location_name + '-review' in featureFlag_locations_entry:
                    new_locations.append('review')
                elif self.location_name + '-publish' in featureFlag_locations_entry:
                    new_locations.append('publish')
            if new_locations == []:
                new_location = 'hidden'
            else:
                new_location = ','.join(new_locations)

        else:
            new_location = 'hidden'

        if not featureFlag_name == new_location:

            newJSON.append({
                "name": featureFlag_name,
                "location": new_location
            })

    topicContents = json.dumps(newJSON, indent=2)

    return (topicContents)
