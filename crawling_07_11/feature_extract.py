from chromeless import Chromeless
from boto3.session import Session

session = Session(aws_access_key_id='<YOUR ACCESS KEY ID>',
                  aws_secret_access_key='<YOUR SECRET KEY>',
                  region_name='<REGION NAME>')
X_path_for_test="""#newsstand"""


def good_wrapper(self):
  self.get("https://google.com")
  return self.get_screenshot_as_png()
  # return image in binary format.

chrome = Chromeless(boto3_session=session)
chrome.attach(good_wrapper)
png = chrome.good_wrapper()
# then write then image down locally.
with open("screenshot.png", 'wb') as f:
    f.write(png)

