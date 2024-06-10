## GPT Image Describer

**Quickly add titles & keywords to photos!**

**Not for Production!** (Uses free OpenAI tier)

**How to Use:**

1. Save script as `images_describer.py`
2. Install dependencies `pip install -r requirements.txt`
3. Get OpenAI key: [https://openai.com/](https://openai.com/) (store in `openai_key.txt`)
4. Run: `python images_describer.py [source folder] [optional destination]`

**Example:**

```
python images_describer.py /mypics /modified
```

**Details:**

* Uses image's "ImageDescription" metadata (if present).
* Free OpenAI tier may have limitations.

**For educational purposes only!**