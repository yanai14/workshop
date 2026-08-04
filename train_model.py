import torch
from torch.utils.data import DataLoader, TensorDataset
from tqdm import tqdm
import timm
from sklearn.kernel_approximation import Nystroem
from sklearn.linear_model import SGDOneClassSVM
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
import numpy as np
from sympy.tensor import tensor



def feture_extract(m,X,batch=32):
    m.eval()
    loader = DataLoader(
        TensorDataset(X),
        batch_size=batch,
        shuffle=False,
    )

    features = []

    with torch.no_grad():
        for (x,) in tqdm(loader, desc="Extracting features"):
            features.append(m(x))

    return torch.cat(features).cpu().numpy()

random_state=42
path_train=r".\yot_bot_type1\_unified_pics\yot_all_train.npy"
path_test=r".\yot_bot_type1\_unified_pics\yot_all_test.npy"

m = timm.create_model('mobilenetv4_conv_small.e2400_r224_in1k', pretrained=True, num_classes=0,in_chans=1)
m.eval()

X_train=np.load(path_train)
X_test=np.load(path_test)
X_train = torch.from_numpy(X_train).unsqueeze(1).float()
X_test = torch.from_numpy(X_test).unsqueeze(1).float()
X_train=feture_extract(m,X_train)
X_test=feture_extract(m,X_test)

print(f'Unpooled shape: {X_train.shape}')
scaler = StandardScaler()

X_train=scaler.fit_transform(X_train)
X_test=scaler.transform(X_test)




# OCSVM hyperparameters
nu = 0.05
gamma = 2.0

# Fit the One-Class SVM using a kernel approximation and SGD
transform = Nystroem(gamma=gamma, random_state=random_state)
clf_sgd = SGDOneClassSVM(
    nu=nu, shuffle=True, fit_intercept=True, random_state=random_state, tol=1e-4,verbose=1
)
pipe_sgd = make_pipeline(transform, clf_sgd)
pipe_sgd.fit(X_train)
y_pred_train_sgd = pipe_sgd.predict(X_train)
y_pred_test_sgd = pipe_sgd.predict(X_test)
#y_pred_outliers_sgd = pipe_sgd.predict(X_outliers)
n_error_train_sgd = y_pred_train_sgd[y_pred_train_sgd == -1].size
n_error_test_sgd = y_pred_test_sgd[y_pred_test_sgd == -1].size
#n_error_outliers_sgd = y_pred_outliers_sgd[y_pred_outliers_sgd == 1].size