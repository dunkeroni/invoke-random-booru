from invokeai.invocation_api import (
    BaseInvocation,
    InputField,
    InvocationContext,
    invocation,
    StringOutput,
    UIComponent,
)

#import pyyaml
import requests
import json

# get api_key from settings.yaml
#settings = pyyaml.load(open("settings.yaml", "r"))
#api_key = settings["api_key"]

@invocation("random-booru",
            title="Random Booru Tags",
            tags=["prompt","caption"],
            category="prompt",
            version="1.1.1",
        )
class RandomBooruInvocation(BaseInvocation):
    limit: int = InputField(
        title="Limit",
        description="The max number of tags to return (-1 for no limit)",
        default=-1,
    )
    filtered: str = InputField(
        title="Filtered",
        description="The tags to filter out",
        default="bad_hands, censored, guro, scat, vomit, loli, shota, school",
        ui_component=UIComponent.Textarea,
    )
    partial_filtering: bool = InputField(
        title="Partial Filtering",
        description="If true, tags that include any of the filtered strings will be removed",
        default=True,
    )

    def request_random_booru_tags(self, limit: int) -> str:
        domain = "https://danbooru.donmai.us" #"https://testbooru.donmai.us/"
        endpoint = "/posts/random.json"
        url = domain + endpoint
        params = {}
        headers = {
            "User-Agent": "dunkeroni-tag-grabber",
            "Accept": "application/json",
        }
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        response = response.json()
        return response
    
    def invoke(self, context: InvocationContext) -> StringOutput:
        limit = self.limit
        filtered = self.filtered
        partial_filtering = self.partial_filtering
        response = self.request_random_booru_tags(limit)
        #convert json to string
        general_tags = response["tag_string_general"]
        character_tags = response["tag_string_character"]
        artist_tags = response["tag_string_artist"]

        print(f"general tags: {general_tags}")
        print(f"character tags: {character_tags}")
        print(f"artist tags: {artist_tags}")

        #replace spaces with commas
        general_tags = general_tags.replace(" ", ", ")

        #change parentheses into escape characters
        general_tags = general_tags.replace("(", "\(")
        general_tags = general_tags.replace(")", "\)")

        #we now have a string in the form of "tag1, tag2, tag3, ..."
        #we can split this string into a list of tags
        general_tags = general_tags.split(", ")
        #if limit is -1, we return all tags
        if limit > -1:
            #otherwise, we return the first limit tags
            general_tags = general_tags[:limit]
        
        #filter out any tags that are in the filtered list
        if self.filtered != "":
            filtered = filtered.split(", ")
            filtered_general_tags = []
            for tag in general_tags:
                for filter in filtered:
                    if partial_filtering and tag.find(filter) != -1:
                        filtered_general_tags.append(tag) if tag not in filtered_general_tags else None
                        break
                    elif filter == tag:
                        filtered_general_tags.append(tag) if tag not in filtered_general_tags else None
                        break
        
            #DEBUG: print out any tags that were filtered
            print(f"filtered tags: {filtered_general_tags}")
            general_tags = [tag for tag in general_tags if tag not in filtered_general_tags]
        
        #join back into a string
        general_tags = ", ".join(general_tags)

        #remove underscores
        general_tags = general_tags.replace("_", " ")

        print(f"final tags: {general_tags}")
        
        return StringOutput(value=general_tags)