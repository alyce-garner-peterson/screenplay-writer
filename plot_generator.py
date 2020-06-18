def generate_plot(np,torch,tokenizer,model,PPLM,bag_of_words,length,no_of_samples):
    raw_text = "SCENE 1 : "
    tokenized_cond_text = tokenizer.encode(
        tokenizer.bos_token + raw_text,
        add_special_tokens=False
    )
    bow_indices = [[tokenizer.encode(word.strip(),add_prefix_space=True,add_special_tokens=False) for word in words] for words in bag_of_words]
    loss_type = PPLM.PPLM_BOW
    pert_gen_tok_texts = []
    discrim_losses = []
    losses_in_time = []
    #print("Starting Conditional Text Generator!.........")
    for i in range(no_of_samples):
        pert_gen_tok_text, discrim_loss, loss_in_time = PPLM.generate_text_pplm(
            model=model,
            tokenizer=tokenizer,
            context=tokenized_cond_text,
            device="cpu",
            perturb=True,
            bow_indices=bow_indices,
            classifier=None,
            class_label=None,
            loss_type=loss_type,
            length=length,
            stepsize=0.03,
            temperature=1.0,
            top_k=10,
            sample=True,
            num_iterations=3,
            grad_length=10000,
            horizon_length=1,
            window_length=5,
            decay=False,
            gamma=1.5,
            gm_scale=0.95,
            kl_scale=0.01,
            verbosity_level=0
        )
        pert_gen_tok_texts.append(pert_gen_tok_text)
        losses_in_time.append(loss_in_time)
    output_text = []
    for i,pert_gen_tok_text in enumerate(pert_gen_tok_texts):
        try:
            pert_gen_text = tokenizer.decode(pert_gen_tok_text.tolist()[0])
            output_text.append(pert_gen_text.replace("<|endoftext|>","").replace("\n",". ").replace("SCENE 1 : ","").strip())
        except:
            pass
    return output_text

def initialize(np,torch):
    from transformers import GPT2Tokenizer
    from transformers.modeling_gpt2 import GPT2LMHeadModel
    import PPLM.run_pplm as PPLM

    torch.manual_seed(0)
    np.random.seed(0)

    model = GPT2LMHeadModel.from_pretrained(
        "gpt2-medium",
        output_hidden_states=True
    )
    model.to("cpu")
    model.eval()
    for param in model.parameters():
        param.requires_grad = False

    tokenizer = GPT2Tokenizer.from_pretrained("gpt2-medium")
    return tokenizer,model,PPLM

if __name__=="__main__":
    import numpy as np
    import torch

    tokenizer,model,PPLM = initialize(np,torch)
    while(True):
        k = int(input("Enter the Length required : "))
        if k<=0:
            break
        print(generate_plot(np,torch,tokenizer,model,PPLM,[["house","morning","cattle"]],k,1))