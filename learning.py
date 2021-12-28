#%%
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from typing import Optional, Union, List
import cv2
import logging
import pandas as pd
import os

logging.basicConfig(level=logging.INFO)
from math import floor
import PIL
from tempfile import TemporaryDirectory

PICTURES_FOLDER = Path(__file__).parent / "profile_pictures"
PICTURES_PROCESSING_FOLDER = PICTURES_FOLDER / "processing"
MODEL_FOLDER = PICTURES_PROCESSING_FOLDER / "models"
PICTURES_PROCESSING_FOLDER.mkdir(exist_ok=True)

if not PICTURES_FOLDER.is_dir():
    raise FileNotFoundError(f"Couldn't find the profile_pictures folder {PICTURES_FOLDER}")

CATEGORIES_FILE = PICTURES_FOLDER / "categories.xml"


def parse_categories_xml_file(
    categories_file: Union[Path, str], pictures_root_folder: Optional[Union[Path, str]] = None, substitute_pictures_root: bool = False
) -> pd.DataFrame:
    pictures_root_folder = Path(pictures_root_folder) if pictures_root_folder is not None else None
    tree = ET.parse(categories_file)
    root = tree.getroot()

    categories = list({keyword_el.text for keyword_el in root.findall("FileList/File/Keywords")})

    rows = []
    for file_el in root.findall("FileList/File"):
        file_path = Path(file_el.attrib["filename"])
        file_name = file_path.name
        if substitute_pictures_root:
            if pictures_root_folder is not None:
                file_path = pictures_root_folder / file_name
            else:
                raise ValueError("pictures_root_folder cannot be None")
        if file_name.endswith(".jpg"):
            if not file_path.is_file():
                logging.error(f"Couldn't find image {file_path}")
                continue

            image = cv2.imread(str(file_path))
            file_categories = defaultdict(int)
            for keyword_el in file_el.findall("Keywords"):
                file_categories[keyword_el.text] = 1
            embeddings = [file_categories[category] for category in categories]
            row = [str(file_path)] + [str(file_name)] + embeddings + [image.shape[0], image.shape[1]]
            rows.append(row)

    df = pd.DataFrame.from_records(rows, columns=["filepath"] + ["filename"] + categories + ["height", "width"])

    return df


#%%
def process_images(
    df: pd.DataFrame, output_dir: Path = PICTURES_PROCESSING_FOLDER, min_height: Optional[int] = None, min_width: Optional[int] = None
) -> pd.DataFrame:
    df["is_file"] = df["filepath"].apply(os.path.isfile)
    df = df[df["is_file"]]

    if min_height is not None:
        df = df[df["height"] >= min_height]
    if min_width is not None:
        df = df[df["width"] >= min_width]

    for image_path in df["filepath"]:
        original_image = PIL.Image.open(image_path)
        crop_height = original_image.shape[0] if min_height is None else min_height
        crop_width = original_image.shape[1] if min_width is None else min_width
        cropped_image = original_image.crop((0, 0, crop_width, crop_height))
        cropped_image_path = output_dir / Path(image_path).name
        cropped_image.save(str(cropped_image_path))

    df["filepath"] = df["filename"].apply(lambda filename: os.path.join(output_dir, filename))

    return df


# %%


def process_and_normalize_image(
    image_path: Path,
    mean: Tuple[float, float, float],
    std: Tuple[float, float, float],
    min_height: Optional[int] = None,
    min_width: Optional[int] = None,
):
    original_image = PIL.Image.open(image_path)
    original_height, original_width = original_image.size[0], original_image.size[1]

    crop_height = original_height if min_height is None else min_height
    crop_width = original_width if min_width is None else min_width
    cropped_image = original_image.crop((0, 0, crop_width, crop_height))

    # return (cropped_image - mean) / std
    return cropped_image


# %%



#%%
df = parse_categories_xml_file(categories_file=CATEGORIES_FILE, pictures_root_folder=PICTURES_FOLDER, substitute_pictures_root=True)
df = process_images(
    df,
    min_height=floor(df["height"].quantile(q=0.1)),
    min_width=floor(df["width"].quantile(q=0.1)),
)


#%%
print(df)

# In[]
from fastai.vision import *

label_col = "yes"
bs = 8
im_size = 128
df = df[["filename", label_col]]
print(df)
imagenet_stats = ([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
data = ImageDataBunch.from_df(
    path=PICTURES_PROCESSING_FOLDER, df=df, valid_pct=0.2, seed=42, fn_col="filename", label_col=label_col, bs=bs, size=im_size
).normalize(imagenet_stats)
learn = cnn_learner(data, models.resnet34, metrics=error_rate)
print(data)

# %%
data.show_batch(rows=3, figsize=(7, 6))
# %%
print(data.classes)
# %%

# %%
learn.fit_one_cycle(2)
#
# %%
learn.save("stage-1-tinder")
# %%

interp = ClassificationInterpretation.from_learner(learn)

losses, idxs = interp.top_losses()

len(data.valid_ds) == len(losses) == len(idxs)
# %%
interp.plot_top_losses(9, figsize=(15, 11))
# %%
learn.lr_find()


# In[ ]:


learn.recorder.plot()

# %%
interp.plot_confusion_matrix(figsize=(12, 12), dpi=60)

# %%
learn.unfreeze()
# %%
learn.fit_one_cycle(1)
# %%
from fastai.basic_train import load_learner

# learn.export()
learn = load_learner(MODEL_FOLDER)

#%%

for pa in PICTURES_FOLDER.glob("*.jpg"):
    cropped_image = process_and_normalize_image(
        PICTURES_FOLDER / pa.name, mean=imagenet_stats[0], std=imagenet_stats[1], min_height=im_size, min_width=im_size
    )

    im = Image(pil2tensor(cropped_image,dtype= np.float32)).normalize(imagenet_stats)

    y ,  pred, raw_pred = learn.predict(im)

    print(pa.name, raw_pred)
# %%
