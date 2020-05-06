import math
import torch
import torch.nn.functional as F

def get_entid(ent_id_file):
    entity2id = {}
    # with open('umls_embed/entity2id.txt') as fin:
    # with open('kg_embed/entity2id.txt') as fin:
    with open(ent_id_file) as fin:
        fin.readline()
        for line in fin:
            qid, eid = line.strip().split('\t')
            entity2id[qid] = int(eid)
    return entity2id
            

def get_ents(ann,ent_map):
    ents = []
    # Keep annotations with a score higher than 0.3
    for a in ann.get_annotations(0.3):
        if a.entity_title not in ent_map:
            continue
        ents.append([ent_map[a.entity_title], a.begin, a.end, a.score])
    return ents

def subbatch(toks, maxlen):
    _, DLEN = toks.shape[:2]
    SUBBATCH = math.ceil(DLEN / maxlen)
    S = math.ceil(DLEN / SUBBATCH) if SUBBATCH > 0 else 0 # minimize the size given the number of subbatch
    stack = []
    if SUBBATCH == 1:
        return toks, SUBBATCH
    else:
        for s in range(SUBBATCH):
            stack.append(toks[:, s*S:(s+1)*S])
            if stack[-1].shape[1] != S:
                nulls = torch.zeros_like(toks[:, :S - stack[-1].shape[1]])
                stack[-1] = torch.cat([stack[-1], nulls], dim=1)
        return torch.cat(stack, dim=0), SUBBATCH


def un_subbatch(embed, toks, maxlen):
    BATCH, DLEN = toks.shape[:2]
    SUBBATCH = math.ceil(DLEN / maxlen)
    if SUBBATCH == 1:
        return embed
    else:
        embed_stack = []
        for b in range(SUBBATCH):
            embed_stack.append(embed[b*BATCH:(b+1)*BATCH])
        embed = torch.cat(embed_stack, dim=1)
        embed = embed[:, :DLEN]
        return embed

#used for bimpm weights
def init_Parameters(views,hidden_size):  
    parameters = []
    for i in range(8):
        parameters.append(torch.nn.Parameter(torch.rand(views,hidden_size)))
    return parameters


def init_kernels(kernel_num):
    MUS = []
    SIGMAS = []
    sigma = 0.01
    exact_sigma = 0.001
    for i in range(kernel_num):
        mu = 1. / (kernel_num - 1) + (2. * i) / (kernel_num - 1) - 1.0
        if mu > 1.0:
            sigma = exact_sigma
            mu = 1.0
        MUS.append(mu)
        SIGMAS.append(sigma)
    return MUS,SIGMAS
    
class Attention(torch.nn.Module):
    """
    Attention module.
    :param input_size: Size of input.
    :param mask: An integer to mask the invalid values. Defaults to 0.
    Examples:
        >>> import torch
        >>> attention = Attention(input_size=10)
        >>> x = torch.randn(4, 5, 10)
        >>> x.shape
        torch.Size([4, 5, 10])
        >>> attention(x).shape
        torch.Size([4, 5])
    """

    def __init__(self, input_size = 100, mask = 0):
        """Attention constructor."""
        super().__init__()
        self.linear = torch.nn.Linear(input_size, 1, bias=False)
        self.mask = mask

    def forward(self, x):
        """Perform attention on the input."""
        x = self.linear(x).squeeze(dim=-1)
        mask = (x != self.mask)
        x = x.masked_fill(mask == self.mask, -float('inf'))
        return F.softmax(x, dim=-1)

class Matching(torch.nn.Module):
    """
    Module that computes a matching matrix between samples in two tensors.
    :param normalize: Whether to L2-normalize samples along the
        dot product axis before taking the dot product.
        If set to `True`, then the output of the dot product
        is the cosine proximity between the two samples.
    :param matching_type: the similarity function for matching
    Examples:
        >>> import torch
        >>> matching = Matching(matching_type='dot', normalize=True)
        >>> x = torch.randn(2, 3, 2)
        >>> y = torch.randn(2, 4, 2)
        >>> matching(x, y).shape
        torch.Size([2, 3, 4])
    """

    def __init__(self, normalize= False, matching_type = 'dot'):
        """:class:`Matching` constructor."""
        super().__init__()
        self._normalize = normalize
        self._validate_matching_type(matching_type)
        self._matching_type = matching_type

    @classmethod
    def _validate_matching_type(cls, matching_type: str = 'dot'):
        valid_matching_type = ['dot', 'mul', 'plus', 'minus', 'concat']
        if matching_type not in valid_matching_type:
            raise ValueError(f"{matching_type} is not a valid matching type, "
                             f"{valid_matching_type} expected.")

    def forward(self, x, y):
        """Perform attention on the input."""
        length_left = x.shape[1]
        length_right = y.shape[1]
        if self._matching_type == 'dot':
            if self._normalize:
                x = F.normalize(x, p=2, dim=-1)
                y = F.normalize(y, p=2, dim=-1)
            return torch.einsum('bld,brd->blr', x, y)
        else:
            x = x.unsqueeze(dim=2).repeat(1, 1, length_right, 1)
            y = y.unsqueeze(dim=1).repeat(1, length_left, 1, 1)
            if self._matching_type == 'mul':
                return x * y
            elif self._matching_type == 'plus':
                return x + y
            elif self._matching_type == 'minus':
                return x - y
            elif self._matching_type == 'concat':
                return torch.cat((x, y), dim=3)    
    
class PACRRConvMax2dModule(torch.nn.Module):

    def __init__(self, shape, n_filters, k, channels):
        super().__init__()
        self.shape = shape
        if shape != 1:
            self.pad = torch.nn.ConstantPad2d((0, shape-1, 0, shape-1), 0)
        else:
            self.pad = None
        self.conv = torch.nn.Conv2d(channels, n_filters, shape)
        self.activation = torch.nn.ReLU()
        self.k = k
        self.shape = shape
        self.channels = channels

    def forward(self, simmat):
        BATCH, CHANNELS, QLEN, DLEN = simmat.shape
        if self.pad:
            simmat = self.pad(simmat)
        conv = self.activation(self.conv(simmat))
        top_filters, _ = conv.max(dim=1)
        top_toks, _ = top_filters.topk(self.k, dim=2)
        result = top_toks.reshape(BATCH, QLEN, self.k)
        return result


class SimmatModule(torch.nn.Module):

    def __init__(self, single=False,padding=-1):
        super().__init__()
        self.single = single
        self.padding = padding
        self._hamming_index_loaded = None
        self._hamming_index = None

    def forward(self, query_embed, doc_embed, query_tok, doc_tok):
        simmat = []

        if self.single:
            a_emb = query_embed
            b_emb = doc_embed
            
            BAT, A, B = a_emb.shape[0], a_emb.shape[1], b_emb.shape[1]

            # embeddings -- cosine similarity matrix
            a_denom = a_emb.norm(p=2, dim=2).reshape(BAT, A, 1).expand(BAT, A, B) + 1e-9 # avoid 0div
            b_denom = b_emb.norm(p=2, dim=2).reshape(BAT, 1, B).expand(BAT, A, B) + 1e-9 # avoid 0div
            perm = b_emb.permute(0, 2, 1)
            sim = a_emb.bmm(perm)
            sim = sim / (a_denom * b_denom)

            # nullify padding (indicated by -1 by default)
            nul = torch.zeros_like(sim)
            sim = torch.where(query_tok.reshape(BAT, A, 1).expand(BAT, A, B) == self.padding, nul, sim)
            sim = torch.where(doc_tok.reshape(BAT, 1, B).expand(BAT, A, B) == self.padding, nul, sim)

            simmat.append(sim)
        else:
            for a_emb, b_emb in zip(query_embed, doc_embed):
                BAT, A, B = a_emb.shape[0], a_emb.shape[1], b_emb.shape[1]

                # embeddings -- cosine similarity matrix
                a_denom = a_emb.norm(p=2, dim=2).reshape(BAT, A, 1).expand(BAT, A, B) + 1e-9 # avoid 0div
                b_denom = b_emb.norm(p=2, dim=2).reshape(BAT, 1, B).expand(BAT, A, B) + 1e-9 # avoid 0div
                perm = b_emb.permute(0, 2, 1)
                sim = a_emb.bmm(perm)
                sim = sim / (a_denom * b_denom)

                # nullify padding (indicated by -1 by default)
                nul = torch.zeros_like(sim)
                sim = torch.where(query_tok.reshape(BAT, A, 1).expand(BAT, A, B) == self.padding, nul, sim)
                sim = torch.where(doc_tok.reshape(BAT, 1, B).expand(BAT, A, B) == self.padding, nul, sim)

                simmat.append(sim)
        return torch.stack(simmat, dim=1)


class DRMMLogCountHistogram(torch.nn.Module):
    def __init__(self, bins):
        super().__init__()
        self.bins = bins

    def forward(self, simmat, dtoks, qtoks):
        # THIS IS SLOW ... Any way to make this faster? Maybe it's not worth doing on GPU?
        BATCH, CHANNELS, QLEN, DLEN = simmat.shape
        # +1e-5 to nudge scores of 1 to above threshold
        bins = ((simmat + 1.000001) / 2. * (self.bins - 1)).int()
        # set weights of 0 for padding (in both query and doc dims)
        weights = ((dtoks != -1).reshape(BATCH, 1, DLEN).expand(BATCH, QLEN, DLEN) * \
                  (qtoks != -1).reshape(BATCH, QLEN, 1).expand(BATCH, QLEN, DLEN)).float()

        # no way to batch this... loses gradients here. https://discuss.pytorch.org/t/histogram-function-in-pytorch/5350
        bins, weights = bins.cpu(), weights.cpu()
        histogram = []
        for superbins, w in zip(bins, weights):
            result = []
            for b in superbins:
                result.append(torch.stack([torch.bincount(q, x, self.bins) for q, x in zip(b, w)], dim=0))
            result = torch.stack(result, dim=0)
            histogram.append(result)
        histogram = torch.stack(histogram, dim=0)

        # back to GPU
        histogram = histogram.to(simmat.device)
        return (histogram.float() + 1e-5).log()


class KNRMRbfKernelBank(torch.nn.Module):
    def __init__(self, mus=None, sigmas=None, dim=1, requires_grad=True):
        super().__init__()
        self.dim = dim
        kernels = [KNRMRbfKernel(m, s, requires_grad=requires_grad) for m, s in zip(mus, sigmas)]
        self.kernels = torch.nn.ModuleList(kernels)

    def count(self):
        return len(self.kernels)

    def forward(self, data):
        return torch.stack([k(data) for k in self.kernels], dim=self.dim)


class KNRMRbfKernel(torch.nn.Module):
    def __init__(self, initial_mu, initial_sigma, requires_grad=True):
        super().__init__()
        self.mu = torch.nn.Parameter(torch.tensor(initial_mu), requires_grad=requires_grad)
        self.sigma = torch.nn.Parameter(torch.tensor(initial_sigma), requires_grad=requires_grad)

    def forward(self, data):
        adj = data - self.mu
        return torch.exp(-0.5 * adj * adj / self.sigma / self.sigma)

def init_KnrmConvModule(n_grams,in_channels,out_channels):
    q_convs = torch.nn.ModuleList()
    d_convs = torch.nn.ModuleList()
    for i in range(n_grams):
        conv = torch.nn.Sequential(
            torch.nn.ConstantPad1d((0,i),0),
            torch.nn.Conv1d(
                in_channels = in_channels,
                out_channels = out_channels,
                kernel_size = i+1
            ),
            torch.nn.ReLU()
        )
        q_convs.append(conv)
        d_convs.append(conv)
    return q_convs,d_convs