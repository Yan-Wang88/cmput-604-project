import scipy.stats as st
import numpy as np

# get alice basis vs bob basis
data = []
with open('log_files/alice_basis_vs_bob_basis.log', 'r') as f:
    lines = f.readlines()

    for line in lines:
        try:
            d = float(line)
        except ValueError:
            continue

        data.append(d)

interval = st.t.interval(alpha=0.95, df=len(data)-1, loc=np.mean(data), scale=st.sem(data)) 
print('mean:', np.mean(data))
print('95 interval:', interval)

# get alice key vs bob key
data_t = []
data_f = []
with open('log_files/alice_key_vs_bob_key.log', 'r') as f:
    lines = f.readlines()

    for line in lines:
        line = line.split(',')
        try:
            d = float(line[0])
            if line[1].strip() == 'True':
                data_t.append(d)
            else:
                data_f.append(d)
        except ValueError:
            continue

        data.append(d)

interval_t = st.t.interval(alpha=0.95, df=len(data_t)-1, loc=np.mean(data_t), scale=st.sem(data_t)) 
interval_f = st.t.interval(alpha=0.95, df=len(data_f)-1, loc=np.mean(data_f), scale=st.sem(data_f)) 
print('mean_t:', np.mean(data_t))
print('mean_f:', np.mean(data_f))
print('95 interval_t:', interval_t)
print('95 interval_f:', interval_f)
print('eves:', len(data_t))


# get alice sample bits vs bob sample bits
data_t = []
data_f = []
with open('log_files/alice_sample_bits_vs_bob_sample_bits.log', 'r') as f:
    lines = f.readlines()

    for line in lines:
        line = line.split(',')
        try:
            d = float(line[0])
            if line[1].strip() == 'True':
                data_t.append(d)
            else:
                data_f.append(d)
        except ValueError:
            continue

        data.append(d)

interval_t = st.t.interval(alpha=0.95, df=len(data_t)-1, loc=np.mean(data_t), scale=st.sem(data_t)) 
interval_f = st.t.interval(alpha=0.95, df=len(data_f)-1, loc=np.mean(data_f), scale=st.sem(data_f)) 
print('mean_t:', np.mean(data_t))
print('mean_f:', np.mean(data_f))
print('95 interval_t:', interval_t)
print('95 interval_f:', interval_f)
print('eves:', len(data_t))
