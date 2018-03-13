# March-Madness
Neural Networks for March Madness
![bracket](2018/img/final_selection_with_games_to_watch.png)

Games highlighted in green were predicted to be within 2 points.

## About the Model
The model uses a dense neural network with the following
feature values from kenpom. The final Network had a structure of
**76 features per game -> 64 relu -> 32 relu -> 1 linear**
These are the features used
* RankAdjOE
* RankAdjDE
* RankAdjTempo
* RankAPL_Off
* RankAPL_Def
* RankeFG_Pct
* RankDeFG_Pct
* RankTO_Pct
* RankDTO_Pct
* RankOR_Pct
* RankDOR_Pct
* RankFT_Rate
* RankDFT_Rate
* RankDFT_Rate
* RankFG3Pct
* RankFG3Pct&od=d
* RankFG2Pct
* RankFG2Pct&od=d
* RankFTPct
* RankFTPct&od=d
* RankBlockPct
* RankBlockPct&od=d
* RankStlRate
* RankStlRate&od=d
* RankF3GRate
* RankF3GRate&od=d
* RankARate
* RankARate&od=d
* RankOff_3
* RankDef_3
* RankOff_2
* RankDef_2
* RankOff_1
* RankDef_1
* RankSOSO
* RankSOSD
* ExpRank
* SizeRank

To play a "game" we append the two teams feature vectors and the network
learns the final score with positive values if the first team won.
We "play" the game in both orientations and average the results.

## Model Performance
We classify based on the sign of the result **74%** of games correctly given a
random holdout.

For core prediction we get a pearson r^2 of 0.5 from a random split holdout set,
bootstrapped and averaged over 5 trials.
![scatter](2018/img/scores_scatter.png)

We see very good enrichment and trend, but the vertical gap is still large.

## Feature Importance
After throwing the model through [LIME](https://homes.cs.washington.edu/~marcotcr/blog/lime/)
for model interpretability the most important features were Adjusted Offensive Efficiency,
Strength of Schedule Offense, and Strength of Schedule Defense.
![feature importance](2018/img/feature_importance.png)


## Play Ins
**Radford**,LIU+Brooklyn,10.799

**Arizona+St.**,Syracues,1.744

**UCLA**,St.+Bonaventure,4.364

**Texas+Southern**,North+Carolina+Central,11.077

## Round of 64
**Virginia**,UMBC,+50.04451592108355

**Creighton**,Kansas+St.,+3.908303406211406

**Kentucky**,Davidson,+10.89758270602971

**Arizona**,Buffalo,+18.140865279997122

**Miami+FL**,Loyola+Chicago,+4.6991498023253815

**Tennessee**,Wright+St.,+37.97860674390514

**Nevada**,Texas,+1.6296466716587592

**Cincinnati**,Georgia+St.,+33.18235395071431

**Xavier**,Texas+Southern,+53.02173634186801

Missouri,**Florida+St.**,+0.7446368598679279

**Ohio+St.**,South+Dakota+St.,+20.824863990904994

**Gonzaga**,UNC+Greensboro,+24.81450266042138

**Houston**,San+Diego+St.,+8.105907868467542

**Michigan**,Montana,+21.672028144920677

**Texas+A%26M**,Providence,+9.095085901651814

**North+Carolina**,Lipscomb,+43.74951632510049

**Villanova**,Radford,+50.874744571093984

**Virginia+Tech**,Alabama,+1.9627672575345292

**West+Virginia**,Murray+St.,+23.108640272034535

**Wichita+St.**,Marshall,+30.0327492265292

**Florida**,UCLA,+10.306061838223519

**Texas+Tech**,Stephen+F.+Austin,+36.575208521755265

Arkansas,**Butler**,+1.2448602147690788

**Purdue**,Cal+St.+Fullerton,+48.65379301536019

**Kansas**,Penn,+41.87121014626839

**Seton+Hall**,North+Carolina+St.,+2.017437224300789

**Clemson**,New+Mexico+St.,+10.553824921393982

**Auburn**,College+of+Charleston,+36.3202287448894

**TCU**,Arizona+St.,+8.563119344566275

**Michigan+St.**,Bucknell,+35.83092858415495

Rhode+Island,**Oklahoma**,+4.057165616991521

**Duke**,Iona,+48.921869093891296


## Round of 32
**Virginia**,Creighton,+17.2533268112181

**Kentucky**,Arizona,+0.41280988841590405

Miami+FL,**Tennessee**,+9.399217535508221

Nevada,**Cincinnati**,+12.524173116373932

**Xavier**,Florida+St.,+7.392531908130084

Ohio+St.,**Gonzaga**,+1.5711283506994658

Houston,**Michigan**,+9.26761663470071

Texas+A%26M,**North+Carolina**,+11.55029332069043

**Villanova**,Virginia+Tech,+19.782516437256362

**West+Virginia**,Wichita+St.,+5.036144138786303

Florida,**Texas+Tech**,+4.623142747846049

Butler,**Purdue**,+15.530353660840754

**Kansas**,Seton+Hall,+10.71568322104881

Clemson,**Auburn**,+1.8494664020168847

TCU,**Michigan+St.**,+8.91185894039101

Oklahoma,**Duke**,+22.765595874341365


## Round of 16
**Virginia**,Kentucky,+16.109263732784186

Tennessee,**Cincinnati**,+5.672054925662727

**Xavier**,Gonzaga,+1.0260055473114418

Michigan,**North+Carolina**,+2.3533056540444743

**Villanova**,West+Virginia,+9.391366389602517

Texas+Tech,**Purdue**,+4.656839870649254

**Kansas**,Auburn,+3.9922927068908898

Michigan+St.,**Duke**,+5.069948109473464


## Round of 8
**Virginia**,Cincinnati,+3.9591254763772836

Xavier,**North+Carolina**,+4.826211384037187

**Villanova**,Purdue,+3.2962636263517306

Kansas,**Duke**,+10.188324621956593


## Round of 4
**Virginia**,North+Carolina,+5.530815293259253

**Villanova**,Duke,+0.7090796229393145

## Round of 2
**Virginia**,Villanova,+0.09199991762398306


## Misc Notes
The feature vector we have is lacking in a number of ways.

### Missing Features
We can add home field advantage in this scheme fairly easily.  I also didn't
encode defensive fingerprint data from kenpom as a one-hot encoded value.

## Player Values
These team fingerprints are also a snapshot in time, they don't cover things
like players going on and coming back from injury.
