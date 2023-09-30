import torch
from pathlib import Path
from ...CLAP-Git.CLAP-interpretable-predictions-main.src.architecture.clap import CLAP

RESULTS_DIR = Path("../CLAP-Git/resolution64")

#from .chestxray import ROOT_DIR
ROOT_DIR = Path("../ NIHCC_CRX_Full_Res / CXR8")

###### Load the Data

LABELS = {
    "Atelectasis": 0,
    "Cardiomegaly": 1,
    "Consolidation": 2,
    "Edema": 3,
    "Effusion": 4,
    "Emphysema": 5,
    "Fibrosis": 6,
    "Hernia": 7,
    "Infiltration": 8,
    "Mass": 9,
    "No Finding": 10,
    "Nodule": 11,
    "Pleural_Thickening": 12,
    "Pneumonia": 13,
    "Pneumothorax": 14,
}


class RandomChestXRay(VisionDataset):
    def __init__(
        self,
        train: bool = False,
        transforms: Optional[Callable] = None,
        transform: Optional[Callable] = None,
        target_transform: Optional[Callable] = None,
        num_random_lines = 2,
    ) -> None:
        super().__init__(str(ROOT_DIR), transforms, transform, target_transform)
        self.train = train

        self.filename, self.y = self._load_data()

    def _load_data(self) -> Union[List, np.ndarray]:
        idx_file = (
            ROOT_DIR / "train_val_list.txt"
            if self.train
            else ROOT_DIR / "test_list.txt"
        )
        with open(idx_file, "r") as file:
            images = set(map(lambda s: s.strip("\n"), random.sample(file.readlines(), num_random_lines)))
        info_df = pd.read_csv(
            ROOT_DIR / "Data_Entry_2017_v2020.csv", index_col="Image Index"
        )

        # select only images selected randomly in the test split
        info_df = info_df[info_df.index.isin(images)]
        filename = list(info_df.index)

        # extract labels
        info_df["Finding Labels"] = info_df["Finding Labels"].map(
            lambda label: label.split("|")
        )

        y = np.zeros((len(filename), len(LABELS)), dtype=np.int8)
        for i, (image_file, (index, row)) in enumerate(
            zip(filename, info_df.iterrows())
        ):
            assert index == image_file
            for disease in row["Finding Labels"]:
                y[i, LABELS[disease]] = 1

        return filename, y

    def __len__(self) -> int:
        return len(self.filename)

    def __getitem__(self, index: int) -> Any:
        y = self.y[index, ...]

        img_file = self.filename[index]
        x = PIL.Image.open(ROOT_DIR / "images" / "images" / img_file)

        if self.transform is not None:
            x = self.transform(x)

        if self.target_transform is not None:
            y = self.target_transform(y)

        return x, y


###### Load the Model

# Create an instance of the VAE model

Clap = CLAP()


# Load the model weights from the checkpoint file

checkpoint_path = RESULTS_DIR/"model_best.pth.tar.gz" 
checkpoint = torch.load(checkpoint_path)
vae.load_state_dict(checkpoint['state_dict'])

###### Encode Data


