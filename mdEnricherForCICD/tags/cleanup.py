def cleanup(cleanup_flags_and_content, cleanup_flags_not_content, source_dir):

    import json
    import os
    import re

    def loop(flag_list, removeContent, topicContents):
        for flag in flag_list:
            if '<' + flag + '>' in topicContents:
                if removeContent is True:
                    print('Removing flag and content: ' + flag)
                    sectionList = re.findall('<' + flag + '>' + '.*?' + '</' + flag + '>', topicContents, flags=re.DOTALL)
                    for section in sectionList:
                        if section + '\n\n' in topicContents:
                            topicContents = topicContents.replace(section + '\n\n', '')
                        else:
                            topicContents = topicContents.replace(section, '')
                else:
                    print('Removing flag: ' + flag)
                    topicContents = topicContents.replace('<' + flag + '>', '')
                    topicContents = topicContents.replace('</' + flag + '>', '')
            else:
                print(flag + ' not used in this topic.')
        return (topicContents)

    if cleanup_flags_and_content is not None:
        if ',' in cleanup_flags_and_content:
            cleanup_flags_and_content_list = cleanup_flags_and_content.split(',')
        else:
            cleanup_flags_and_content_list = [cleanup_flags_and_content]

    if cleanup_flags_not_content is not None:
        if ',' in cleanup_flags_not_content:
            cleanup_flags_not_content_list = cleanup_flags_not_content.split(',')
        else:
            cleanup_flags_not_content_list = [cleanup_flags_not_content]

    print('\nCleaning up feature flags in the Markdown Enricher.')
    for (path, dirs, files) in os.walk(source_dir):
        # TO DO: Only handle supported filetypes
        if ('.git' not in path) and ('/images' not in path):
            for file in files:
                print('\n\n' + path + '/' + file)
                with open(path + '/' + file, 'r', encoding="utf8", errors="ignore") as fileName_read:
                    if file == 'feature-flags.json':
                        try:
                            topicContentsJSON = json.load(fileName_read)
                        except Exception as e:
                            print('feature_flag.json could not be loaded.')
                            topicContents = fileName_read.read()
                            print(e)
                        else:
                            if cleanup_flags_and_content is not None:
                                for flag in cleanup_flags_and_content_list:
                                    for idx, obj in enumerate(topicContentsJSON):
                                        if obj['name'] == flag:
                                            topicContentsJSON.pop(idx)
                                            print('Removed flag: ' + flag)
                                            break
                            if cleanup_flags_not_content is not None:
                                for flag in cleanup_flags_not_content_list:
                                    for idx, obj in enumerate(topicContentsJSON):
                                        if obj['name'] == flag:
                                            topicContentsJSON.pop(idx)
                                            print('Removed flag: ' + flag)
                                            break
                            topicContents = str(json.dumps(topicContentsJSON, indent=4))
                    else:
                        topicContents = fileName_read.read()
                        if cleanup_flags_and_content is not None:
                            removeContent = True
                            topicContents = loop(cleanup_flags_and_content_list, removeContent, topicContents)
                        if cleanup_flags_not_content is not None:
                            removeContent = False
                            topicContents = loop(cleanup_flags_not_content_list, removeContent, topicContents)
                with open(path + '/' + file, 'w+', encoding="utf8", errors="ignore") as fileName_write:
                    fileName_write.write(topicContents)
